import paho.mqtt.client as mqtt
import time
import random
import statistics as stats

broker_address = "localhost"
broker_port = 1883
keep_alive = 60
client = mqtt.Client('Sensor_Temperatura')
client.connect(broker_address, broker_port, keep_alive)
topic = "Broker/Piscina/Sensores/Temperatura"

global temperatura
temperatura= []

while True:
    temp= random.uniform(15,30)
    print("%.2f"%temp)
    temperatura.append(temp)
    client.publish(topic,"%.2f"% temp,1)
    time.sleep(3)
    client.loop()
