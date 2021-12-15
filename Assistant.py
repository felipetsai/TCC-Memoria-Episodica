import pika
import sys

# Inicializar a mensageria
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='modulo', exchange_type='direct')
    return channel, connection

# Postar uma mensagem na fila
def SendMessage(message,key):
    if (key == "a"):
        print(" Sending Message to queue %r" % key, message[3:])
    else:
        print(" Sending Message to queue %r" % key, message)
    channel.basic_publish(exchange='modulo', routing_key= key, body=message)

# Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

# Identifica a mensagem e encaminha para o modulo correto.
def Send_message(ch, method, properties, body):
    data = body.decode('utf-8')
    if(type(data) == list):
        Send_message(data,"r")
    else:
        SendMessage(data[1:],data[0])

# Recebe mensagem.
def Receive_message():
    print(' [*] Waiting messages. To exit press CTRL+C')

    channel.basic_consume(
        queue=queue_name, on_message_callback=Send_message, auto_ack=True)
    channel.start_consuming()
    
def Main():
    global channel
    global queue_name
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='main', queue=queue_name)
    Receive_message()

Main()