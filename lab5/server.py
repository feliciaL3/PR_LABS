import socket
import threading
import json

# server conf
HOST = '127.0.0.1'
PORT = 12345

# create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

# dict for connected  clients
connected_clients = {}

# for client messages
def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        try:
            message = json.loads(data)
            message_type = message.get('type')

            if message_type == "connect":
                handle_connection(client_socket, message)
            elif message_type == "message":
                handle_message(client_socket, message)
        except json.JSONDecodeError:
            print("Invalid JSON received from client.")

#remove client from connected_clients dict after disconnecting
    if client_socket in connected_clients:
        del connected_clients[client_socket]

    client_socket.close()

def handle_connection(client_socket, message):
    client_name = message['payload']['name']
    room_name = message['payload']['room']

    connected_clients[client_socket] = {
        'name': client_name,
        'room': room_name
    }

    response = {
        "type": "connect_ack",
        "payload": {
            "message": "Connected to the room."
        }
    }
    client_socket.send(json.dumps(response).encode('utf-8'))

def handle_message(client_socket, message):
    sender = connected_clients[client_socket]['name']
    room_name = connected_clients[client_socket]['room']
    text = message['payload']['text']

    for client, info in connected_clients.items():
        if info['room'] == room_name:
            response = {
                "type": "message",
                "payload": {
                    "sender": sender,
                    "room": room_name,
                    "text": text
                }
            }
            client.send(json.dumps(response).encode('utf-8'))

    print(f"Broadcasted message from {sender} in room {room_name}: {text}")

clients = []

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)

    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()


