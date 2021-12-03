import cv2
import pika
import sys
import time
import numpy as np

def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def StopPubSub(connection):
    connection.close()

#Enviar imagem delimitada para assistant
def SendImage(message):
    message = "e"+message
    print(" Face Detected %r" % message[1:])
    channel.basic_publish(exchange='main', routing_key='', body=message)

def RecognizeFace(ch, method, properties, body):
    filename = body.decode('utf-8')
    print(" [x] %r" % filename)
    i = 0
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Ler imagem da fila.
    img = cv2.imread(filename)
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    if ( len(faces) > 0 ):
        for (x, y, w, h) in faces:
            #Delimitar rosto
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi = img[y:y+h, x:x+w]
            img_item = "faces/face" + filename[13] + "_" + str(i) + ".png"
            i += 1
            cv2.imwrite(img_item, roi)
            SendImage(img_item)
    # Caso não encontre rosto na imagem.
    else:
        print("No Face Detected")

def Receive_message():
    print(' [*] Waiting for Images. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=RecognizeFace, auto_ack=True)
    channel.start_consuming()

def Main():
    global channel
    global queue_name
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key = 'f')
    Receive_message()
Main()