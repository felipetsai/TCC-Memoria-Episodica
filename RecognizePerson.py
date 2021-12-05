import cv2
import pika
import sys
from simple_facerec import SimpleFacerec
import time

#Iniciar a mensageria
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

#Carregar as imagens de rostos para posterior reconhecimento.
def LoadFace():
    sfr = SimpleFacerec()
    sfr.load_encoding_images("Sample_image/")
    return sfr

#Postar uma mensagem na mensageria
def SendPerson(message,filename):
    id = filename[10]
    message = "ap"+id+message
    print(" Person Detected %r" % message[2:], filename)
    channel.basic_publish(exchange='main', routing_key='', body=message,
                properties=pika.BasicProperties(content_type='text/plain',
                                                          app_id='test',
                                                          timestamp=int(time.time()),
                                                          delivery_mode=1))
    
#Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

#função callback é chamado assim que receber uma mensagem da fila
def RecognizePerson(ch, method, properties, body):
    filename = body.decode('utf-8')
    # Ler imagem da fila.
    img = cv2.imread(filename)
    face_locations, face_names = sfr.detect_known_faces(img)
    if (len(face_names) > 0):
        SendPerson(face_names[0],filename)

#Receber imagem do rosto delimitado
def Receive_Image():
    print(' [*] Waiting for Images. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=RecognizePerson, auto_ack=True)
    channel.start_consuming()

def main():
    global id
    global channel
    global sfr
    global queue_name
    sfr = LoadFace()
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key = 'e')
    Receive_Image()
main()