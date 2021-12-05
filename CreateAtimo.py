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
_person = []
_emotion =  []
_restaurant =  []
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
    _idimage = data[1]
    value = data[2:]
    print("image: ", _idimage)
    print(type)
    print(_idimage)
    global _atimo 
    global _emotion
    global _person
    global _restaurant
    exist = False
    index = 0

    if (type == "p"): ### atimo pessoa
        #Se o átimo já está na lista
        for i in range(len(_person)):
            if (value == _person[i].value):
                _person[i].end = time.time()
                index = i
                exist = True
                break
        
        if (exist == False):
            _person.append(Atimo(_atimo,value,time.time(),time.time(),_idimage,[]))
            _atimo += 1

            # quando a emoção e pessoa vem da mesma imagem
            for e in range(len(_emotion)):
                if (_person[index].idImage == _emotion[e].idImage):
                    _person[index].relation.append(_emotion[e].number)

            # quando a pessoa e restaurante vem da mesma imagem
            for r in range(len(_restaurant)):
                if (_person[index].idImage == _restaurant[r].idImage):
                    _person[index].relation.append(_restaurant[r].number)
                
    elif (type == "e"): ### atimo emocao
        #Se o átimo já está na lista
        for e in range(len(_emotion)):
            if (value == _emotion[e].value):
                _emotion[e].end = time.time()
                index = e
                exist = True
                break
        
        if (exist == False):
            _emotion.append(Atimo(_atimo,value,time.time(),time.time(),_idimage,[]))
            _atimo += 1
            
            for i in range(len(_person)):
                if (_person[i].idImage == _emotion[index].idImage):
                    _person[i].relation.append(_emotion[index].number)


    elif (type == "g"): ### atimo restaurante
        #Se o átimo já está na lista
        for r in range(len(_restaurant)):
            if (value == _restaurant[r].value):
                _restaurant[r].end = time.time()
                index = r
                exist = True
                break
        
        if (exist == False):          
            _restaurant.append(Atimo(_atimo,value,time.time(),time.time(),_idimage,[]))
            _atimo += 1
            
            for i in range(len(_person)):
                if (_person[i].idImage == _restaurant[index].idImage):
                    _person[i].relation.append(_restaurant[index].number)
           

             
    listIndex = []
    # Verifica atimos na memória de curto prazo
    for r in range(len(_restaurant)):     
        if (time.time() - _restaurant[r].end > 120): #2min
            query = _restaurant[r].CreateQuery()
            SendQuery("g"+query)
            listIndex.append(_restaurant[r])
    
    for i in listIndex:
        _restaurant.remove(i)
    
    
    listIndex = []
    for e in range(len(_emotion)):     
        if (time.time() - _emotion[e].end > 120): #2min
            query = _emotion[e].CreateQuery()
            SendQuery("e"+query)
            listIndex.append(_emotion[e])
    
    for i in listIndex:
        _emotion.remove(i)
    
    listIndex = []
    for p in range(len(_person)):
        if (time.time() - _person[p].end > 120): #2min
            query = _person[p].CreateQuery()
            SendQuery("p"+query)
            listIndex.append(_person[p])
        
    for i in listIndex:
        _person.remove(i)

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