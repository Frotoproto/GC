from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store usernames and messages
usernames = {}
messages = []

# Load censor list from a file
def load_censor_list(file_path='censor_list.txt'):
    """
    Loads the censor list from a file.
    """
    try:
        with open(file_path, 'r') as file:
            return [line.strip().lower() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Warning: Censor list file '{file_path}' not found. Using an empty list.")
        return []

CENSOR_LIST = load_censor_list()

def censor_message(message):
    """
    Replaces banned words in the message with asterisks (case-insensitive).
    """
    for word in CENSOR_LIST:
        message = re.sub(re.escape(word), '*' * len(word), message, flags=re.IGNORECASE)
    return message

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_send_message(data):
    username = data['username']
    message = data['message']
    if username not in usernames:
        usernames[username] = True
        emit('username_assigned', {'username': username}, broadcast=True)
    # Censor the message before broadcasting
    censored_message = censor_message(message)
    full_message = {'username': username, 'message': censored_message}
    messages.append(full_message)
    emit('receive_message', full_message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)