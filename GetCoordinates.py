import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace
import pika
import sys
import time

#Iniciar a mensageria
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

#Postar uma mensagem na mensageria
def SendRestaurant(message,filename):
    message = "ag"+message
    print(" Location Detected %r" % message[2:])
    channel.basic_publish(exchange='main', routing_key='', body=message,
                properties=pika.BasicProperties(content_type='text/plain',
                                                          app_id='test',
                                                          headers={'img': filename},
                                                          timestamp=int(time.time()),
                                                          delivery_mode=1))
    
#Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

#função GetCoordinates é chamado assim que receber uma mensagem da fila
def GetCoordinates(ch, method, properties, body):
    filename = body.decode('utf-8')
    restaurant = 'outback'
    SendRestaurant(restaurant,filename)


def Receive_message():
    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=GetCoordinates, auto_ack=True)
    channel.start_consuming()
    
def Main():
    global queue_name
    global channel
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='f')
    Receive_message()
Main()