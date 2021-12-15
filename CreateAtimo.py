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
    def __init__(self, number, classe, value, start, end, relation):
        self.number = number
        self.classe = classe
        self.value = value
        self.start = start
        self.end = end
        self.relation = relation

    def CreateQuery(self):
        query = "PREFIX db1: <http://example.com/restaurantes/> \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:class \"" + self.classe +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:value \"" + str(self.value) +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:start " + str(self.start) +"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:end " + str(self.end) +"} }; \n"
        
        listRelation = list(dict.fromkeys(self.relation))
        for r in listRelation:
            query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:related db1:at" + str(r) + "} }; \n"
        return query
    
class Restaurant:
    def __init__(self,idImage, restaurant, people):
        self.idImage = idImage
        self.restaurant = restaurant
        self.people = people
    
class Person:
    def __init__(self,idPerson,person,emotion):
        self.idPerson = idPerson
        self.person = person
        self.emotion = emotion
    
# Variaveis Globais
_restaurant =  Restaurant(0,Atimo(0,"restaurant",0,0,0,[]),[])
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
    _idperson = data[1:3]
    value = data[3:]
    #print("body:", data)
    print("Id: ", _idperson)
    print(type)
    global _atimo 
    global _emotion
    global _person
    global _restaurant
    exist = False
    index = 0

    if (type == "p"): ### atimo pessoa
        #Se o átimo já está na lista
        for i in range(len(_restaurant.people)):
            if (_restaurant.people[i].person.value == value):
                _restaurant.people[i].person.end = time.time()
                _restaurant.people[i].idPerson = _idperson
                exist = True
                break
        
        if (exist == False):
            _restaurant.people.append(Person(_idperson,Atimo(_atimo,"person",value,time.time(),time.time(),[_restaurant.restaurant.number]),Atimo(0,"emotion",0,0,0,[])))
            _atimo += 1

                
    elif (type == "e"): ### atimo emocao
        #Se o átimo já está na lista
        for i in range(len(_restaurant.people)):
            if (_idperson == _restaurant.people[i].idPerson):
                if (_restaurant.people[i].emotion.value == value):
                    _restaurant.people[i].emotion.end = time.time()
                else:
                    if (_restaurant.people[i].emotion.value != 0):
                        SendQuery("e"+ _restaurant.people[i].emotion)
                    _restaurant.people[i].emotion = Atimo(_atimo,"emotion",value, time.time(),time.time(),[])
                    _atimo += 1
                    _restaurant.people[i].person.relation.append(_restaurant.people[i].emotion.number)

                break


    elif (type == "g"): ### atimo restaurante
        #Se o átimo já está na lista
        
        _restaurant.idImage = _idimage## novo idimage
        
        if (_restaurant.restaurant.value == value):
            _restaurant.restaurant.end = time.time()
        
        else:
            if _restaurant.restaurant.value != 0:
                SendQuery("g"+_restaurant.restaurant.CreateQuery())
                
            _restaurant.restaurant = Atimo(_atimo,"restaurant",value,time.time(),time.time(),[])
            _atimo += 1
            
            for i in range(len(_restaurant.people)):
                if (_restaurant.people[i].idPerson[:-1] == _restaurant.idImage):
                    _restaurant.people[i].person.relation.append(_restaurant.restaurant.number)
 

             
    listIndex = []
    # Verifica atimos na memória de curto prazo    
    for p in range(len(_restaurant.people)):
        if (time.time() - _restaurant.people[p].person.end > 30): #2min
            SendQuery("p"+_restaurant.people[p].person.CreateQuery())
            SendQuery("e"+_restaurant.people[p].emotion.CreateQuery())
            listIndex.append(_restaurant.people[p])
        
    for i in listIndex:
        _restaurant.people.remove(i)

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