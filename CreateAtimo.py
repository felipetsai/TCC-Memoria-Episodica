# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import time
import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace
import pika
import sys

# Objeto Átimo

class Atimo:
    def __init__(self, number, classe, value, start, end, relation, idImage):
        self.number = number
        self.classe = classe
        self.value = value
        self.start = start
        self.end = end
        self.relation = relation
        self.idImage = idImage

    def CreateQuery(self):
        query = "PREFIX db1: <http://example.com/restaurantes/> \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:class \"" + self.classe +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:value \"" + self.value +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:start " + str(self.start) +"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:end " + str(self.end) +"} }; \n"
        
        for r in self.relation:
            query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:related db1:at" + str(r) + "} }; \n"
        return query
    
# Variaveis Globais
_person = Atimo(0,"person","",0,0,[],"")
_emotion =  Atimo(0,"emotion","",0,0,[],"")
_restaurant =  Atimo(0,"restaurant","",0,0,[],"")
_atimo = 1

def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def SendQuery(message):
    message = "q"+message
    print(" [x] Sent %r" % message)
    channel.basic_publish(exchange='main', routing_key='', body=message)
    
    
def StopPubSub(connection):
    connection.close()

def CreateAtimo(ch, method, properties, body):
    data = body.decode('utf-8')
    type = data[0]
    value = data[1:]
    _idimage = properties.header.get('img')
    print(type)
    print(_idimage)
    global _atimo 
    global _emotion
    global _person
    global _restaurant

    if (type == "p"): ### atimo pessoa
        #Se o átimo já está na lista
        if (value == _person.value):
            _person.end = time.time()
        else:
            # caso ainda tenha pessoa na memória de curto prazo
            if(_person.number != 0):
                query = _person.CreateQuery()
                SendQuery("p"+query)
            
            _person.number = _atimo
            _person.value = value
            _person.start = time.time()
            _person.end = time.time()
            _person.idImage = _idimage
            _atimo += 1
        
            # quando a emoção e pessoa vem da mesma imagem
            if (_person.idImage == _emotion.idImage):
                _person.relation.append(_emotion.number)
                _person.relation.append(_restaurant.number)
            # quando a pessoa e restaurante vem da mesma imagem
            if (_person.idImage == _restaurant.idImage):
                _person.relation.append(_restaurant.number)
                
    elif (type == "e"): ### atimo emocao
        #Se o átimo já está na lista
        if (value == _emotion.value):
            _emotion.end = time.time()
        else:
            # caso ainda tenha emoção na memória de curto prazo
            if(_emotion.number != 0):
                query = _emotion.CreateQuery()
                SendQuery("e"+query)
            _emotion.number = _atimo
            _emotion.value = value
            _emotion.start = time.time()
            _emotion.end = time.time()
            _emotion.idImage = _idimage
            _atimo += 1
            if (_person.idImage == _emotion.idImage):
                _person.relation.append(_emotion.number)

    elif (type == "g"): ### atimo restaurante
        #Se o átimo já está na lista
        if (value == _restaurant.value):
            _restaurant.end = time.time()
        else:
            query = _restaurant.CreateQuery()
            SendQuery("g"+query)
            _restaurant.number = _atimo
            _atimo += 1
            
            if (_person.idImage == _restaurant.idImage):
                _person.relation.append(_restaurant.number)
    
def Main():
    global channel
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='a')
    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=CreateAtimo, auto_ack=True)
    channel.start_consuming()

Main()