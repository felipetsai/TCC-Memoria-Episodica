import pika
import sys
import ast

class Restaurant:
    def __init__(self, restaurant, numberofvisits, emotion, lastvisit):
        self.restaurant = restaurant
        self.numberofvisits = numberofvisits
        self.emotion = emotion
        self.lastvisit = lastvisit

# Inicializar a mensageria
def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

# Finalizar a mensageria
def StopPubSub(connection):
    connection.close()

# Postar uma mensagem na fila
def SendRestaurant(message):
    print("Restaurant Selected: %r", message)
    message = "j"+ message
    channel.basic_publish(exchange='main', routing_key= '', body=message)

# Seleciona o restaurante
def SelectMemory(ch, method, properties, body):
    data = body.decode('utf-8')
    list = ast.literal_eval(data)
    print(list)
    listRestaurants = []
    for result in list:
        listRestaurants.append(Restaurant(result["Restaurant"]["value"],result["Numberofvisits"]["value"],result["EmotionSum"]["value"],result["LastVisited"]["value"]))
    
    restaurant = [-1,""]
    for event in listRestaurants:
        if int(event.emotion) > restaurant[0]:
            restaurant[0] = int(event.emotion) 
            restaurant[1] = event.restaurant
    
    restaurantSelected = restaurant[1]
    SendRestaurant(restaurantSelected)

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

    channel.queue_bind(exchange='modulo', queue=queue_name, routing_key='r')
    Receive_message()

Main()
    