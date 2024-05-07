import struct
import paho.mqtt.client as mqtt

broker_address = "localhost"
broker_port = 1883
topic = "silverline/pendulum/pos_act"

def publish_double(topic, value):
    client = mqtt.Client()

    client.connect(broker_address, broker_port)

    binary_data = struct.pack('d', value)

    client.publish(topic, binary_data)

    client.disconnect()

if __name__ == "__main__":
    value_to_publish = 0.09

    publish_double(topic, value_to_publish)
