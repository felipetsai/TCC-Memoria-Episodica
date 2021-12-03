import cv2
import pika
import sys

def StartCam():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")
    return cam

def StopCam(cam):
    cam.release()
    cv2.destroyAllWindows()

def StartPubSub():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='main', exchange_type='fanout')
    return channel, connection

def SendMessage(message):
    message = "f"+message
    channel.basic_publish(exchange='main', routing_key='', body=message)
    print(" [x] Sending %r" % message[1:])
    
def StopPubSub(connection):
    connection.close()

def TakePic():
    img_counter = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "Images/frame_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            SendMessage(img_name)
            # Postar uma mensagem na fila com o nome da imagem.

def Main():
    global channel
    global cam
    cam = StartCam()
    channel, connection = StartPubSub()
    TakePic()
    StopCam(cam)

Main()