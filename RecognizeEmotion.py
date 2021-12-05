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
def SendMessage(message,filename):
    id = filename[10]
    message = "ae"+id+message
    print(" Emotion Detected: %r" % message[3:] , filename)
    channel.basic_publish(exchange='main', routing_key='', body=message,
                properties=pika.BasicProperties(content_type='text/plain',
                                                          app_id='test',
                                                          timestamp=int(time.time()),
                                                          delivery_mode=1))
    
#Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

#função RecognizeEmotion é chamado assim que receber uma mensagem da fila
def RecognizeEmotion(ch, method, properties, body):
    filename = body.decode('utf-8')
    img = cv2.imread(filename)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    predictions = DeepFace.analyze(img)
    SendMessage(predictions['dominant_emotion'],filename)

# Recebe imagem do rosto
def Receive_Image():
    print(' [*] Waiting for faces. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=RecognizeEmotion, auto_ack=True)
    channel.start_consuming()

def Main():
    global id
    global channel
    global queue_name
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='e')
    Receive_Image()
Main()