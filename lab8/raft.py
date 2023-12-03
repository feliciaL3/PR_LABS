# raft.py
import json
import socket
from node import Node


class RAFTFactory:
    def __init__(self,
                 service_info: dict,
                 udp_host: str = "127.0.0.1",
                 udp_port: int = 8000,
                 udp_buffer_size: int = 1024,
                 num_followers: int = 2):

        # initializing UDP socket and configuration parameters
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.udp_buffer_size = udp_buffer_size
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.service_info = service_info

        # set minim number of messages to receive
        self.min_num_msgs = num_followers * 2
        try:
            # attempt to bind to the UDP socket indicating that the node is a leader
            self.udp_socket.bind((self.udp_host, self.udp_port))
            self.role = "leader"

            self.followers = []
            count_of_msgs = 0
            # continuously receive messages from followers
            while True:
                message, address = self.udp_socket.recvfrom(self.udp_buffer_size)
                # handle "Accept" messages from followers
                if message.decode() == "Accept":
                    data = json.dumps(self.service_info)
                    count_of_msgs += 1
                    self.udp_socket.sendto(str.encode(data), address)

                else:
                    message = message.decode()
                    count_of_msgs += 1
                    follower_data = json.loads(message)
                    self.followers.append(follower_data)
                # break the loop if enough messages have been received
                if count_of_msgs >= self.min_num_msgs:
                    break
        except:
            # if binding to the UDP socket fails--> the node is a follower
            self.role = "follower"
            # send Accept message to the leader and receive leader's information
            self.leader_data = self.send_accept("Accept")
            self.send_accept(self.service_info)
        # close the UDP socket
        self.udp_socket.close()

    def send_accept(self, msg):
        # meth to send an Accept message to the leader and receive information
        if type(msg) is str:
            bytes_to_send = str.encode(msg)
            self.udp_socket.sendto(bytes_to_send, (self.udp_host, self.udp_port))
            msg_from_server = self.udp_socket.recvfrom(self.udp_buffer_size)[0]
            return json.loads(msg_from_server.decode())
        else:
            str_dict = json.dumps(msg)
            bytes_to_send = str.encode(str_dict)
            self.udp_socket.sendto(bytes_to_send, (self.udp_host, self.udp_port))

    def create_server(self):
        # method to create a Node instance based on the role (leader or follower)
        if self.role == 'leader':
            return Node(True, self.followers)
        else:
            return Node(False)
