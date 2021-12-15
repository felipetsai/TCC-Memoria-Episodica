import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace
import pika
import sys
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import json
import time
import Constraint 

#url = Constraint.DB_Url
url =  "http://DESKTOP-MIOEQ5T:7200/repositories/memory"
_key = ""
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def SendRestaurants(message):
    message = "r" +_key+str(message)
    #print(" Restaurant list: %r" % message)
    channel.basic_publish(exchange='main', routing_key='', body=message)
    
def StopPubSub(connection):
    connection.close()

def SendQuery(ch, method, properties, body):
    data = body.decode('utf-8')
    query = data[1:]
    _key = data[0]
    #print(data)
    sparql = SPARQLWrapper(url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()["results"]["bindings"] 
    print(results)
    SendRestaurants(results)

def ReceiveQuery():
    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=SendQuery, auto_ack=True)
    channel.start_consuming()

def Main():
    global queue_name
    global channel
    global sparql
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='k')
    #sparql = DBConnection
    ReceiveQuery()
    
Main()