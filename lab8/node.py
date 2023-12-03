# node.py
class Node:
    def __init__(self, leader: bool, followers: dict = None) -> None:
        self.users = {}
        self.leader = leader
        if self.leader:
            self.followers = followers

    def print_info(self):
        print(f'Is leader: {self.leader}')
        if self.leader:
            print(f'Followers: {self.followers}')
