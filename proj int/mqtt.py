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

# Callback de connexion MQTT
def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code de retour: " + str(rc))
    client.subscribe(topic)

# Callback de réception de message MQTT
def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print(f"Message reçu sur le topic {msg.topic}: {message}")
    process_message(message)

# Fonction pour traiter les messages reçus
def process_message(message):
    data = {}
    for item in message.split(','):
        key_value = item.split('=')
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            data[key] = value

    # Vérifier si les clés nécessaires sont présentes
    if 'Id' not in data or 'piece' not in data or ('date' not in data and ('time' not in data and 'heure' not in data)) or 'temp' not in data:
        print("Message MQTT incomplet ou mal formé.")
        return

    sensor_id = data['Id']
    piece = data['piece']
    
    # Récupération de la date et de l'heure
    if 'date' in data and 'time' in data:
        timestamp_str = data['date']
        time_str = data['time']
    elif 'date' in data and 'heure' in data:
        timestamp_str = data['date']
        time_str = data['heure']
    else:
        print("Les clés 'date' et 'time'/'heure' ne sont pas présentes dans les données MQTT.")
        return

    try:
        timestamp = datetime.strptime(f"{timestamp_str} {time_str}", "%d/%m/%Y %H:%M:%S")
    except ValueError as e:
        print(f"Erreur lors du parsing de la date/heure : {e}")
        return

    try:
        value = float(data['temp'])
    except ValueError as e:
        print(f"Erreur lors de la conversion de la température en nombre : {e}")
        return

    # Vérifier si le capteur existe déjà pour cette pièce
    if sensor_id not in sensors:
        sensors[sensor_id] = {
            'Nom': sensor_id,
            'Piece': piece,
            'Emplacement': ''  # Si vous ne l'utilisez pas, vous pouvez supprimer cette partie
        }

    try:
        cursor.execute("SELECT id FROM sensor WHERE sensor_id = %s AND piece = %s", (sensor_id, piece))
        existing_sensor = cursor.fetchone()

        if existing_sensor:
            # Capteur existant, ne rien faire ici
            print(f"Capteur {sensor_id} pour la pièce {piece} existe déjà dans la base de données.")
        else:
            # Capteur n'existe pas encore pour cette pièce, l'ajouter
            cursor.execute("INSERT INTO sensor (sensor_id, piece) VALUES (%s, %s)",
                           (sensor_id, piece))
            db.commit()
            print(f"Capteur {sensor_id} inséré dans la base de données pour la pièce {piece}")
    except pymysql.Error as e:
        print(f"Erreur lors de l'insertion ou vérification du capteur {sensor_id} : {e}")
        db.rollback()

    try:
        cursor.execute("INSERT INTO temperaturedata (sensor_id_id, timestamp, value) VALUES (%s, %s, %s)",
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
    client.disconnect()
    cursor.close()
    db.close()
