from typing import List

import paho.mqtt.client as mqtt
import time
import random
import statistics as stats

broker_address = "192.168.1.100"
broker_port = 1883
keep_alive = 60
client = mqtt.Client('Sensor_Cloro')
client.connect(broker_address, broker_port, keep_alive)
topic = "Broker/Piscina/Sensores/Cloro"                 # Publicador

global cloro
cloro= []


def controlValores(client):
    global cloro
    if len(cloro) == 5:
        promedio = ((stats.mean(cloro)))                # calcula la media de los 5 últimos registros introducidos aleatoriamente
        client.publish(topic, "%.2f" %promedio, 1)      # publica en el topic el reultado del promedio
        cloro = []                                      # reinicia el array a 0

while True:
    cl = random.uniform(0,4)                            # introduce númeroa aleatorios entre 0 y 4 a la variable cl
    print("%.2f"%cl)
    cloro.append(cl)                                    # introduce los valores cl en el array  de la variable cloro
    controlValores(client)                              # llamada a la función
    time.sleep(1)                                       # un segundo de retardo en envío
    client.loop()                                       # actualiza conexión
