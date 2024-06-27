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
cursor = db.cursor() # Création d'un curseur pour exécuter des requêtes SQL, (c'est un objet qui permet de parcourir les résultats d'une requête)
sensors = {} # Dictionnaire pour stocker les informations des capteurs, avec l'id du capteur comme clé
messages = [] # Liste pour stocker les messages reçus (pour les écrire dans un fichier)

# Callback de connexion MQTT

def on_connect(client, userdata, flags, rc): # Cclient = client MQTT, userdata = données utilisateur, flags = drapeaux de connexion, rc = code de retour, 0 = connexion établie, 1,2,3,4 = erreur,   
    print("Connecté avec le code de retour: " + str(rc))
    client.subscribe(topic) # "S'abonner" au topic pour recevoir les messages

# Callback de réception de message MQTT
def on_message(client, userdata, msg): # client = client MQTT, userdata = données utilisateur, msg = objet message
    message = msg.payload.decode('utf-8') # Décodage du message en chaîne de caractères (msg.payload est un tableau de bytes)
    print(f"Message reçu sur le topic {msg.topic}: {message}") 
    process_message(message) # Extrait les données du message et les insère dans la base de données
    print(msg.topic + " " + str(msg.payload)) 
    messages.append(msg.topic + " " + str(msg.payload)) 

def write_messages_to_file(messages): # Fonction pour écrire les messages reçus dans un fichier
    with open("messages.txt", "w") as file: # Ouvrir le fichier en mode écriture
        for message in messages: # Parcourir la liste des messages
            file.write(message + "\n") # Écrire le message dans le fichier

# Fonction pour traiter les messages reçu
def process_message(message): 
    data = {} 

    for item in message.split(','): # Parcourir les éléments du message séparés par des virgules
        key, value = item.split('=') # Séparer la clé et la valeur de chaque élément (ex: 'Id=Capteur1' -> key='Id', value='Capteur1')
        data[key.strip()] = value.strip() # Stocker les données dans un dictionnaire 

    sensor_id = data['Id'] # Récupérer l'id du capteur dans le message et le stocker dans la variable sensor_id
    piece = data['piece'] # Meme principe que pour l'id du capteur
    nom = data.get('nom', sensor_id)  # Récupérer le nom du capteur, si non défini, utiliser l'id du capteur

    if sensor_id not in sensors: # Ajout du capteur dans le dictionnaire des capteurs si il n'y est pas déjà
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
    
    timestamp = datetime.strptime(f"{data['date']} {data['time']}", "%d/%m/%Y %H:%M:%S") # Convertir la date et l'heure en objet datetime (datetime est une classe qui permet de manipuler des dates et des heures)
    value = float(data['temp'])

    try:
        cursor.execute("SELECT sensor_id FROM sensor WHERE sensor_id = %s", (sensor_id,)) # Vérifier si le capteur existe déjà dans la base de données
        existing_sensor = cursor.fetchone() # Récupérer le résultat de la requête

        if not existing_sensor: # Si le capteur n'existe pas, l'ajouter dans la table sensor
            cursor.execute("INSERT INTO sensor (sensor_id, nom, piece) VALUES (%s, %s, %s)", (sensor_id, nom, piece))
            db.commit() # Envoyer la requête à la base de données
            print(f"Capteur {sensor_id} ajouté dans la base de données pour la pièce {piece}")
        else:
            print(f"Capteur {sensor_id} existe déjà dans la base de données.") 

        cursor.execute("INSERT INTO temperaturedata (sensor_id, timestamp, value) VALUES (%s, %s, %s)", # inséret les données dans la table temperaturedata
                       (sensor_id, timestamp, value)) 
        db.commit() 
        print("Données insérées avec succès")
    except pymysql.Error as e: # Gestion des erreurs quelconques
        print(f"Erreur lors de l'insertion des données : {e}")
        db.rollback()

# Configuration et lancement du client MQTT

client = mqtt.Client() # Création d'un client MQTT, (c'est un objet qui permet de se connecter à un broker MQTT)
client.on_connect = on_connect # Définition de la fonction de connexion, si la connexion est établie, la fonction on_connect est appelée
client.on_message = on_message # Définition de la fonction de réception de message, si un message est reçu, la fonction on_message est appelée

client.connect(broker, port, 60) # Connexion au broker MQTT

# Boucle de réception des messages MQTT
try:
    print("Démarrage de la boucle MQTT. Appuyez sur Ctrl+C pour arrêter.")
    client.loop_forever() # Boucle infinie pour recevoir les messages

except KeyboardInterrupt: # Gestion de l'interruption par l'utilisateur
    print("Interruption par l'utilisateur. Arrêt du programme.")
    write_messages_to_file(messages) # Écrire les messages reçus dans un fichier
    client.disconnect() # Déconnexion du client MQTT
    cursor.close() # Fermeture du curseur
    db.close() # Fermeture de la connexion à la base de données
