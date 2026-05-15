import socket
import threading

PHONE_IP = '172.23.70.223'  # Change this to your phone's IPv4
PHONE_PORT = 12345         # Change to the Local Port set on phone

# 2. PC Info
PC_IP = '172.23.64.58'    #Change this to your PC IP address(refer readme for how to find it.)    
PC_PORT = 12000            

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((PC_IP, PC_PORT))

def receive_messages():
    # Function to continuously listen for messages.
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"\nDaksh's phone: {data.decode()}")
        except Exception as e:
            print(f"Error receiving: {e}")
            break

def send_messages():
   #Function to handle keyboard input and sending.
    print(f"Chat started! Sending to {PHONE_IP}:{PHONE_PORT}")
    print("-------------------------------------------")
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break
        sock.sendto(msg.encode(), (PHONE_IP, PHONE_PORT))

#Receiver thread
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

#Sending messages
send_messages()