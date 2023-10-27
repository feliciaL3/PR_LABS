from player import Player
import xml.etree.ElementTree as ET
import player_pb2 as PlayerList


class PlayerFactory:
    def to_json(self, players):
        '''
            This function should transform a list of Player objects into a list with dictionaries.
        '''

        return [{
            "nickname": player.nickname,
            "email": player.email,
            "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
            "xp": player.xp,
            "class": player.cls
        } for player in players]

    def from_json(self, list_of_dict):
        '''
            This function should transform a list of dictionaries into a list with Player objects.
        '''
        return [
            Player(player["nickname"], player["email"], player["date_of_birth"], player["xp"], player["class"])
            for player in list_of_dict]

    def from_xml(self, xml_string):
        '''
            This function should transform a XML string into a list with Player objects.
        '''

        root = ET.fromstring(xml_string)

        list_of_players = []

        for data in list(root):
            nickname, email, date_of_birth, xp, classes = [player.text for player in list(data)]
            list_of_players.append(Player(nickname, email, date_of_birth, int(xp), classes))
        return list_of_players

    def to_xml(self, list_of_players):
        '''
            This function should transform a list with Player objects into a XML string.
        '''

        root = ET.Element("data")

        for p in list_of_players:
            player = ET.SubElement(root, "player")
            nickname = ET.SubElement(player, "nickname")
            nickname.text = p.nickname
            email = ET.SubElement(player, "email")
            email.text = p.email
            date_of_birth = ET.SubElement(player, "date_of_birth")
            date_of_birth.text = p.date_of_birth.strftime("%Y-%m-%d")
            xp = ET.SubElement(player, "xp")
            xp.text = str(p.xp)
            classes = ET.SubElement(player, "class")
            classes.text = p.cls

        return ET.tostring(root, "utf-8")

    def from_protobuf(self, binary):
        '''
            This function should transform a binary protobuf string into a list with Player objects.
        '''
        proto_player_list = PlayerList.PlayersList()
        proto_player_list.ParseFromString(binary)
        player_list = []
        for proto_player in proto_player_list.player:
            player_list.append(Player(
                proto_player.nickname,
                proto_player.email,
                proto_player.date_of_birth,
                proto_player.xp,
                PlayerList.Class.Name(proto_player.cls),
            ))

        return player_list

    def to_protobuf(self, list_of_players):
        '''
            This function should transform a list with Player objects intoa binary protobuf string.
        '''
        proto_player_list = PlayerList.PlayersList()
        for p in list_of_players:
            proto_player = proto_player_list.player.add()
            proto_player.nickname = p.nickname
            proto_player.email = p.email
            proto_player.date_of_birth = p.date_of_birth.strftime("%Y-%m-%d")
            proto_player.xp = p.xp
            proto_player.cls = PlayerList.Class.Value(p.cls)

        return proto_player_list.SerializeToString()
