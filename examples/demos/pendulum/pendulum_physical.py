import paho.mqtt.client as mqtt
import time
import struct

class PendulumPhysical:
    def __init__(self, broker_address="localhost", broker_port=1884):
        self.min_position = -0.15
        self.max_position = 0.15

        self.position = None
        self.theta = None

        self.client = mqtt.Client("arena")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(broker_address, broker_port)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[PendulumPhysical] Connected to *local* MQTT broker")
            self.client.subscribe("silverline/pendulum/pos_act")
            self.client.subscribe("silverline/pendulum/theta")
        else:
            print("Failed to connect, return code: ", rc)

    def _on_message(self, client, userdata, msg):
        if msg.topic == "silverline/pendulum/pos_act":
            self.position = struct.unpack('d', msg.payload)[0]
            #  print("Position: ", self.position)
        elif msg.topic == "silverline/pendulum/theta":
            self.theta = struct.unpack('d', msg.payload)[0]

    def _publish(self, topic, payload):
        self.client.publish(topic, payload)

    def set_position(self, position):
        position = max(self.min_position, min(self.max_position, position))
        print("Pos: ", position)
        self._publish("silverline/pendulum/pos_set", struct.pack('d', position))

    def get_rotation(self):
        return self.theta # in radians
