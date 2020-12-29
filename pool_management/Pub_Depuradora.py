import paho.mqtt.client as mqtt
import time
import json
import datetime

broker_address = "localhost"
broker_port = 1883
keep_alive = 60
client = mqtt.Client('Depuradora')
client.connect(broker_address, broker_port, keep_alive)
topic = "Broker/Piscina/Depuradora"
global arrancaManana
global arrancaTarde

def controlDepuradora():

    while True:

        inicioTarde = datetime.time(18, 00, 0)
        finTarde = datetime.time(22, 0, 0)

        inicioManana = datetime.time(10, 0, 0)
        finManana = datetime.time(14, 0, 0)

        horaActual = datetime.datetime.now().time()

        arrancaTarde=(horaActual >= inicioTarde) and (horaActual <= finTarde)
        arrancaManana=(horaActual >= inicioManana) and (horaActual <= finManana)

        if ((arrancaTarde) or (arrancaManana)):

            print("Depuradora encendida")
            payload = json.dumps({"msg": "Depuradora", "estado": 1})
            print("---------------------------------------------")
            client.publish(topic, payload, 1)

        else:

            print("Depuradora apagada")
            payload = json.dumps({"msg": "Depuradora", "estado": 0})
            print("---------------------------------------------")
            client.publish(topic, payload, 1)

        time.sleep(30)
        client.loop()

controlDepuradora()






