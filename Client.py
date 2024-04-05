import socket
import sys
import threading

class Client:
    # Initialize the client
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = None
        self.channel = None

    def start(self):
        self.client.connect((self.host, self.port))
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()
        self.send()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')

                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))

                elif message == 'NICK_DUPLICATE':
                    print('Nickname is already in use. Please choose another one.')
                    self.nickname = input("Enter your nickname: ")
                    self.client.send(self.nickname.encode('ascii'))

                elif message == 'CHANNEL':
                    self.channel = input("Enter the channel you want to join: ")
                    self.client.send(self.channel.encode('ascii'))

                elif message == 'NOT ONLINE':
                    print('The user you want to send a private message to is not online.')

                elif message == 'EXIT':
                    print('You left the chat.')
                    self.client.close()
                    sys.exit(0)
                    break

                else:
                    print(message)

            except:
                sys.exit(0)
                break

    def send(self):
        while True:
            try:
                message = input()
                self.client.send(message.encode('ascii'))
                if message == 'Exit':
                    self.client.send('EXIT'.encode('ascii'))
                    break

            except:
                print('An error occurred!')
                self.client.close()
                break

if __name__ == "__main__":
    client = Client()
    client.nickname = input("Enter your nickname: ")
    client.start()