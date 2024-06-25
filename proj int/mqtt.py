import paho.mqtt.client as mqtt
import pymysql
from datetime import datetime

broker = "test.mosquitto.org"
topic = "IUT/Colmar2024/SAE2.04/Maison1"
port = 1883

# Connexion MySQL
db = pymysql.connect(
    host="localhost",
    user="siteusr",
    password="2503",
    database="SiteCollecte"
)
cursor = db.cursor()

sensors = {}
messages = []

# Callback de connexion MQTT
def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code de retour: " + str(rc))
    client.subscribe(topic)

# Callback de réception de message MQTT
def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print(f"Message reçu sur le topic {msg.topic}: {message}")
    process_message(message)
    print(msg.topic + " " + str(msg.payload))
    messages.append(msg.topic + " " + str(msg.payload))

def write_messages_to_file(messages):
    with open("messages.txt", "w") as file:
        for message in messages:
            file.write(message + "\n")

# Fonction pour traiter les messages reçus0
def process_message(message):
    data = {}

    for item in message.split(','):
        key, value = item.split('=')
        data[key.strip()] = value.strip()

    sensor_id = data['Id']
    piece = data['piece']
    nom = data.get('nom', sensor_id)  # Use sensor_id as nom if 'nom' is not provided in the message

    if sensor_id not in sensors:
        sensors[sensor_id] = {
            'Nom': sensor_id,
            'Piece': piece,
            'Emplacement': ''
        }

    # Vérifier si l'id du capteur est dans la liste des ids à ignorer
    ignore_ids = ['Capteur1', '12A6B8AF6CD3', '12345']
    if sensor_id in ignore_ids:
        print(f"Capteur {sensor_id} ignoré. Ne sera pas inséré dans la base de données.")
        return
    
    timestamp = datetime.strptime(f"{data['date']} {data['time']}", "%d/%m/%Y %H:%M:%S")
    value = float(data['temp'])

    try:
        cursor.execute("SELECT sensor_id FROM sensor WHERE sensor_id = %s", (sensor_id,))
        existing_sensor = cursor.fetchone()

        if not existing_sensor:
            # Capteur n'existe pas encore, l'ajouter dans la table sensor
            cursor.execute("INSERT INTO sensor (sensor_id, nom, piece) VALUES (%s, %s, %s)", (sensor_id, nom, piece))
            db.commit()
            print(f"Capteur {sensor_id} ajouté dans la base de données pour la pièce {piece}")
        else:
            print(f"Capteur {sensor_id} existe déjà dans la base de données.")

        # inséret les données dans la table temperaturedata
        cursor.execute("INSERT INTO temperaturedata (sensor_id, timestamp, value) VALUES (%s, %s, %s)",
                       (sensor_id, timestamp, value))
        db.commit()
        print("Données insérées avec succès")
    except pymysql.Error as e:
        print(f"Erreur lors de l'insertion des données : {e}")
        db.rollback()

# Configuration et lancement du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

# Boucle de réception des messages MQTT
try:
    print("Démarrage de la boucle MQTT. Appuyez sur Ctrl+C pour arrêter.")
    client.loop_forever()
except KeyboardInterrupt:
    print("Interruption par l'utilisateur. Arrêt du programme.")
    write_messages_to_file(messages)
    client.disconnect()
    cursor.close()
    db.close()
