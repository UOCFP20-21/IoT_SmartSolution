import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time

# Número de la farola
numero = 1
sector = 1
estado = 0
now = datetime.now()
encendido = False;
pir = 0


def on_connect(client, userdata, flags, rc):
    print("Sensor conectado: Result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # Nos suscribimos al Broker de la luz en cuestion
    client.subscribe("Broker/Alumbrado/Sector" + str(sector) + "/Luz" + str(numero) + "/#")


def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))

    msgTopic = msg.topic
    msgCoded = msg.payload.decode("utf-8")
    msgCoded = int(msgCoded, 10)

    if msgTopic == "Broker/Alumbrado/Sector" + str(sector) + "/Luz" + str(
            numero) + "/foco":  # Devuelve 1|0 si hay movimiento

        if msgCoded == 1:  # El PIR ha detectado movimiento
            # Arduino activa el PIN corresopondiente para encender la Farola
            print("Encendemos la farola")
        else:
            print("Apagamos la farola")

    if msgTopic == "Broker/Alumbrado/Sector" + str(sector) + "/Luz" + str(
            numero) + "/pir":  # Devuelve 1|0 si hay movimiento

        if msgCoded == 1:  # El PIR ha detectado movimiento
            # Arduino activa el PIN corresopondiente para encender la Farola
            print("Pir detecta movimiento")
        else:
            print("Pir NO detecta movimiento")
    if msgTopic == "Broker/Alumbrado/Sector" + str(sector) + "/Luz" + str(
            numero) + "/pir/estado":  # Devuelve 1|0: Modifica el estado del PIR
        global pir
        if msgCoded == 1:  # El PIR envía estado Activo
            if (pir == 0):
                pir = 1
                print("Pir Cambia su estado a 1")
        else:
            if (pir == 1):
                pir = 0
                print("Pir Cambia su estado a 0")
        client.publish("Broker/Alumbrado/Sector" + str(sector) + "/Luz" + str(numero) + "/pir", pir)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.100", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
while True:
    client.loop()

# client.loop_forever()
