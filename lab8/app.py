# app.py
import sys
import random
import time
import requests
from flask import Flask
from flask import request
from flask import jsonify

from raft import RAFTFactory
from models.database import db
from models.electro_scooter import ElectroScooter

service_info = {
    "host": "127.0.0.1",
    "port": int(sys.argv[1]),
}
# delays the execution of the program for a random duration between 1  3 seconds
time.sleep(random.randint(1, 3))

node = RAFTFactory(service_info).create_server()
node.print_info()

db_name = "electro_scooters"
if not node.leader:
    db_name += f"_{str(random.randint(1, 3))}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}.db'
db.init_app(app)


@app.route('/api/electro-scooters', methods=['POST'])
def create_electro_scooter():
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            data = request.get_json()
            name = data['name']
            battery_level = data['battery_level']

            electro_scooter = ElectroScooter(name=name, battery_level=battery_level)
            db.session.add(electro_scooter)
            db.session.commit()

            if node.leader:
                for follower in node.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/api/electro-scooters",
                                  json=request.json,
                                  headers={"Token": "leader"})

            return jsonify({"message": "Electro Scooter created successfully"}), 201
        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400


@app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
    if scooter is not None:
        return jsonify({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        }), 200
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404


@app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    '''
        This function handles the update requests.
    '''
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                data = request.get_json()
                scooter.name = data.get('name', scooter.name)
                scooter.battery_level = data.get('battery_level', scooter.battery_level)
                db.session.commit()

                if node.leader:
                    for follower in node.followers:
                        requests.put(f"http://{follower['host']}:{follower['port']}/api/electro-scooters/{scooter_id}",
                                     json=request.json,
                                     headers={"Token": "leader"})

                return jsonify({"message": "Electro Scooter updated successfully"}), 200
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    '''
        This function handles the delete requests.
    '''
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                password = request.headers.get('X-Delete-Password')
                if password == 'your_secret_password':
                    db.session.delete(scooter)
                    db.session.commit()

                    if node.leader:
                        for follower in node.followers:
                            requests.delete(
                                f"http://{follower['host']}:{follower['port']}/api/electro-scooters/{scooter_id}",
                                headers={"Token": "leader", "X-Delete-Password": "your_secret_password"})

                    return jsonify({"message": "Electro Scooter deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def init_database():
    with app.app_context():
        db.create_all()
        sample_scooter_1 = ElectroScooter(name="Scooter 1", battery_level=90.5)
        sample_scooter_2 = ElectroScooter(name="Scooter 2", battery_level=80.0)
        db.session.add(sample_scooter_1)
        db.session.add(sample_scooter_2)
        db.session.commit()


if __name__ == "__main__":
    init_database()
    app.run(
        host=service_info["host"],
        port=service_info["port"]
    )
