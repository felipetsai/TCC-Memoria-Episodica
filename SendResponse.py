import pika
import sys

# Inicializar a mensageria
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

# Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

# Comunicação com o usuário
def SendRestaurant(message):
    print("O restaurante selecionado foi:", message)

# Seleciona o restaurante
def SelectMemory(ch, method, properties, body):
    data = body.decode('utf-8')
    #seleciona o restaurante
    SendRestaurant(data[1:])

# lista de restaurante
def Receive_message():
    print("Waiting for restaurants. To exit press CTRL+C")

    channel.basic_consume(
        queue=queue_name, on_message_callback=SelectMemory, auto_ack=True)
    channel.start_consuming()
    
def Main():
    global channel
    global queue_name
    channel, connection = StartPubSub()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='j')
    Receive_message()

Main()
    