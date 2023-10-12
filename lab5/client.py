import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def receive_messages():
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        try:
            message = json.loads(data)
            message_type = message.get('type')

            if message_type == "connect_ack":
                handle_connection_ack(message)
            elif message_type == "message":
                handle_message(message)
            elif message_type == "notification":
                handle_notification(message)
        except json.JSONDecodeError:
            print("Invalid JSON received from server.")


def handle_connection_ack(message):
    message_text = message['payload']['message']
    print(f"Server: {message_text}")


def handle_message(message):
    sender = message['payload']['sender']
    room = message['payload']['room']
    text = message['payload']['text']
    print(f"{room} - {sender}: {text}")


def handle_notification(message):
    notification_text = message['payload']['message']
    print(f"Notification: {notification_text}")


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

name = input("Enter your name: ")
room = input("Enter the room name: ")

connect_message = {
    "type": "connect",
    "payload": {
        "name": name,
        "room": room
    }
}

# send   th connect message to the server
client_socket.send(json.dumps(connect_message).encode('utf-8'))

while True:
    message_text = input("Enter a message (or 'exit' to quit): ")

    if message_text.lower() == 'exit':
        break

    message = {
        "type": "message",
        "payload": {
            "sender": name,
            "room": room,
            "text": message_text
        }
    }

    client_socket.send(json.dumps(message).encode('utf-8'))

client_socket.close()
