import threading
import socket
import json
import os
import uuid
RESET = "\033[0m"
GREEN = "\033[92m"


class ChatClient:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.client_id = str(uuid.uuid4())  # generate a unique client ID
        self.name = input("Enter your name: ").strip()
        self.room = input("Enter the room: ").strip()
        self.CLIENT_DIR = os.path.join('Downloads', f'{self.name}_{self.room}')  # create a client-specific download directory

        os.makedirs(self.CLIENT_DIR, exist_ok=True)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        print(f"Connected to {self.HOST}:{self.PORT}")

        self.connect_to_server()

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def connect_to_server(self):
        # send a connection message to the server
        connect_msg = {
            "type": "connect",
            "payload": {"name": self.name, "room": self.room}
        }
        self.send_message(connect_msg)

    def send_message(self, message):
        try:
            message_json = json.dumps(message).encode('utf-8')
            self.client_socket.send(message_json)
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_messages(self):
        file_name = None
        is_file = False
        while True:
            try:
                message = self.client_socket.recv(1024)
                if not message:
                    print("Connection lost.")
                    break

                if is_file:
                    # receiving a file
                    with open(os.path.join(self.CLIENT_DIR, file_name), 'ab') as file:
                        file.write(message)

                        while True:
                            self.client_socket.settimeout(0.5)
                            try:
                                next_chunk = self.client_socket.recv(1024)
                                if not next_chunk:
                                    break
                                file.write(next_chunk)
                            except socket.timeout:
                                break

                    print(f"File {file_name} - downloaded successfully in {os.path.join(self.CLIENT_DIR, file_name)}.")
                    file_name = None
                    is_file = False
                    self.client_socket.settimeout(None)
                    continue

                message_str = message.decode('utf-8', errors='ignore')

                if message_str.strip().startswith('{') and message_str.strip().endswith('}'):
                    message_json = json.loads(message_str)
                    msg_type = message_json.get('type')

                    if msg_type == 'file_info':
                        file_name = message_json['payload']['name']
                        is_file = True
                    elif msg_type == 'notification':
                        print(message_json['payload']['message'])
                    elif msg_type == 'message':
                        payload = message_json['payload']
                        print(f"{payload['sender']}: {payload['text']}")
                    elif msg_type == 'connect_ack':
                        print(message_json['payload']['message'])
                    elif msg_type == 'error':
                        print(message_json['payload']['message'])

            except Exception as e:
                print(f"Error occurred: {e}")
                break

    def run(self):
        try:
            while True:
                print(GREEN + "Choose your next action: 1. upload:  2. download:  3. exit" + RESET)
                text = input()
                if text.lower() == 'exit':
                    break
                elif text.lower().startswith('upload:'):
                    # uploading a file
                    _, file_path = text.split(':', 1)
                    message = {
                        "type": "upload",
                        "payload": {"path": file_path.strip()}
                    }
                elif text.lower().startswith('download:'):
                    # requesting a file download
                    _, file_name = text.split(':', 1)
                    message = {
                        "type": "download",
                        "payload": {"name": file_name.strip()}
                    }
                else:
                    message = {
                        "type": "message",
                        "payload": {"sender": self.name, "room": self.room, "text": text}
                    }
                self.send_message(message)
        except KeyboardInterrupt:
            print("\nExiting the client.")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 8080
    chat_client = ChatClient(HOST, PORT)
    chat_client.run()
