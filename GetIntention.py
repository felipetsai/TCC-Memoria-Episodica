import pika
import sys


def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def StopPubSub(connection):
    connection.close()

#Converte em query
def SendQuery(query):
    message = "k"+_key+query
    channel.basic_publish(exchange='main', routing_key='', body=message)
    print(" [x] Sent %r" % message)
    
_key = ""
#Converter em query
def CreateQuery():
    query = """
        PREFIX db1: <http://example.com/restaurantes/>

        SELECT (SAMPLE(?restaurant) AS ?Restaurant) 
        (COUNT(?restaurant) AS ?Numberofvisits) 
        (SUM(IF(?emotion = "Positive", 1, IF(?emotion = "Negative", -1, 0))) AS ?EmotionSum)
        (MAX(?date) AS ?LastVisited)
        WHERE
            {
                ?p db1:class "person".
                ?p db1:value "Felipe".
                ?p db1:start ?date.
                ?e db1:class "emotion".
                ?e db1:value ?emotion.
                ?r db1:class "restaurant".
                ?r db1:value ?restaurant.
                ?p db1:related ?r.
                ?p db1:related ?e.
            }
        GROUP BY ?restaurant
        ORDER BY DESC(?Numberofvisits)
                    """
    SendQuery(query)
        
#receber intenção do usuário
def ReceiveIntetion():
    while True:
        _key = input()
        print("input: ", _key)
        CreateQuery()

def Main():
    global channel
    channel, connection = StartPubSub()
    ReceiveIntetion()

Main()