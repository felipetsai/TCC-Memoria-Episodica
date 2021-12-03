import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace
import pika
import sys
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import json
import time
import Constraint 

url = Constraint.DB_Url

    
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def SendMessage(message):
    print(" [x] Sent %r" % message)
    channel.basic_publish(exchange='main', routing_key='', body=message)
    
def StopPubSub(connection):
    connection.close()

#Inserir atimo no banco
def InsertAtimo(ch, method, properties, body):
    data = body.decode('utf-8')
    type = data[0]
    value = data[1:]
    sparql.setQuery(value)
    sparql.method = 'POST'
    sparql.setReturnFormat('json')
    sparql.queryType = "INSERT"
    results = sparql.query()  
    print(results) 

#Conectar no banco
def DBConnection():
    sparql = SPARQLWrapper(url)
    sparql.setHTTPAuth(BASIC)
    return sparql

#Receber query
def ReceiveQuery():
    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=InsertAtimo, auto_ack=True)
    channel.start_consuming()
    
def Main():
    global queue_name
    global channel
    global sparql
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='q')
    
    sparql = DBConnection()
    ReceiveQuery()
Main()