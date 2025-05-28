from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import requests
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow requests from any origin
CORS(app)
# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Define the correct sequence of button IDs for unlocking the vault
password_buttons = ["1", "4", "2", "3"]
# Track progress through the password sequence
enabled_index = 0
# Vault lock state
vault_locked = True

@socketio.on('connect')
def handle_connect():
    """Handle a new client connection over SocketIO."""
    print('Client connected')


def password_completion(pressed_button):
    """
    Check whether the pressed button matches the next expected button in the password sequence.
    Returns True if the full sequence has been entered correctly.
    """
    global enabled_index, password_buttons

    # Advance index if the correct button is pressed
    if pressed_button == password_buttons[enabled_index]:
        enabled_index += 1
    else:
        # Reset index on incorrect button press
        enabled_index = 0
        # If the incorrect press matches the first button in the sequence,
        # treat it as the start of a new attempt
        if pressed_button == password_buttons[0]:
            enabled_index = 1

    # Sequence complete when index matches sequence length
    if enabled_index == len(password_buttons):
        return True
    return False

@app.route('/')
def home():
    """Render the main entry page."""
    return render_template('index.html')

@app.route('/button_click', methods=['POST'])
def button_click():
    """
    Handle a button click event from the front-end.
    If the password sequence is complete, unlock the vault and return additional content.
    """
    global enabled_index
    button_id = request.json.get('button_id')
    print(f"Button clicked: {button_id}")

    if password_completion(button_id):
        print("Vault unlocked")
        # Reset index for next entry attempt
        enabled_index = 0
        # Load hidden webpage section to inject
        with open("hidden_web_page.html", "r") as f:
            new_section = f.read()
        return jsonify({
            "status": "unlocked",
            "button": button_id,
            "password_completion_index": enabled_index,
            "new_section": new_section
        })
    else:
        # Return current progress without revealing content
        return jsonify({
            "status": "in_progress",
            "button": button_id,
            "password_completion_index": enabled_index,
            "new_section": ""
        })

@app.route('/message_send', methods=['POST'])
def message_send():
    """
    Forward a user message to the bot service and return status.
    """
    received_message = request.json.get('message_text')
    print(f"Sending message to bot service: {received_message}")

    try:
        # Post the message to the local bot service endpoint
        response = requests.post(
            "http://127.0.0.1:5001/send_message_pb",
            json={"message": received_message}
        )
        response.raise_for_status()
    except Exception as e:
        print("Error sending message to bot service:", e)
        return jsonify({"status": "error", "error": str(e)}), 500

    return jsonify({"status": "sent"})

@app.route('/messages_refresh', methods=['POST'])
def messages_refresh():
    """
    Retrieve the latest chat messages from the bot service based on requested amount.
    """
    data = request.get_json()
    amount_of_messages = data.get('amt_messages')
    print(f"Refreshing messages; requested count: {amount_of_messages}")

    # Fetch chat history from the bot service
    response = requests.get(
        "http://127.0.0.1:5001/get_chat_history",
        params={'amt_messages': amount_of_messages}
    )
    return jsonify({"messages": response.json()})

@app.route('/bot_forced_update', methods=["POST"])
def bot_forced_update():
    """
    Receive forced update notifications from bot service and emit via SocketIO.
    """
    messages = request.json.get('messages')
    print(f"Bot triggered forced update with messages: {messages}")
    # Notify connected clients to refresh their message list
    socketio.emit('Flask_force_message_update', {'messages': messages})
    return jsonify({"status": "update_emitted"})

if __name__ == '__main__':
    # Run the application with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
