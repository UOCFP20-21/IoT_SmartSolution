import paho.mqtt.client as mqtt
import json
import statistics as stats
import datetime

broker_address = "192.168.1.100"
broker_port = 1883
topic = "Broker/Piscina/#"
global media
media = []


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("UserData= " + str(userdata))
    print("")
    client.subscribe(topic, qos=1)


def on_message(client, userdata, msg):
    print("Topic=", msg.topic)
    print("Mensaje recibido=", str(msg.payload.decode("utf-8")))
    print("Nivel de calidad=", msg.qos)
    print("---------------------------------------------")
    print("")

    msgTopic = msg.topic
    msgMensaje = msg.payload.decode("utf-8")

    if msgTopic == "Broker/Piscina/Sensores/Cloro":
        global media
        inicio = datetime.time(21, 0, 0)
        fin = datetime.time(21, 30, 0)

        horaActual = datetime.datetime.now().time()

        media.append(float(msgMensaje))

        if len(media) == 5:
            prom = ((stats.mean((media))))
            print("La media de la ultima hora es " + str("%.2f" % prom) + " ppm ")
            if ((prom < 1) or (prom > 3)):
                topic = "Sometimes/Piscina/Dosificador/Cloro"

                if ((horaActual > inicio) and (horaActual < fin)):
                    print("Bomba dosificadora encendida")
                    payload = json.dumps({"msg": "Bomba dosificacion encendida", "estado": 1})
                    print("---------------------------------------------")
                    client.publish(topic, payload, 1)
                else:
                    topic = "Sometimes/Piscina/Cloro"

                    print("Bomba apagada")
                    # payload=json.dumps({"msg":"Bomba dosificacion apagada ","estado":0})
                    payload = json.dumps({"msg": "Cloro alto,bomba apagada ", "nivel": prom})
                    print("Horario de baño")
                    print(horaActual)
                    print("---------------------------------------------")
                    client.publish(topic, payload, 1)
            else:
                topic = "Sometimes/Piscina/Dosificador/Cloro"
                print("Bomba dosificadora Apagada")
                payload = json.dumps({"msg": "Bomba dosificacion apagada", "estado": 0})
                print("---------------------------------------------")
                print("")
                client.publish(topic, payload, 1)
            media = []


client = mqtt.Client('Cliente1', userdata="Sometimes")
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, broker_port, 60)
client.loop_forever()
