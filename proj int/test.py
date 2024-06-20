import paho.mqtt.client as mqtt

broker = "test.mosquitto.org"
topic = "IUT/Colmar2024/SAE2.04/Maison1"
port = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    messages.append(msg.topic + " " + str(msg.payload))

def write_messages_to_file(messages):
    with open("messages.txt", "w") as file:
        for message in messages:
            file.write(message + "\n")

messages = []

try:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_forever()
except KeyboardInterrupt:
    print("Fin du programme")
    client.disconnect()
    write_messages_to_file(messages)