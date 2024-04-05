import socket
import threading

class ChatServer:
    # Initialize the server
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.nicknames = {}
        self.channels = {}

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f'Server is listening on port number {self.port} and address {self.host}')
        while True:
            client_socket, client_address = self.server.accept()
            print(f'[+] Successfully connected to {str(client_address)}...')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client):
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        while nickname in self.nicknames.values():
            print('Nickname is already in use.')
            client.send('NICK_DUPLICATE'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')

        self.nicknames[client] = nickname
        self.clients[nickname] = client

        client.send('CHANNEL'.encode('ascii'))
        channel = client.recv(1024).decode('ascii')

        self.channels[nickname] = channel

        print(f'[+] Nickname of the client is {nickname}')
        print(f'[+] Channel of the client is {channel}')
        client.send("[+] Connected to the server...".encode('ascii'))
        client.send("\nTo send a Private message, enter 'Private message'".encode('ascii'))
        client.send("\nTo quit, enter 'Exit' ".encode('ascii'))
        client.send("\nEnter your message or choice below: ".encode('ascii'))

        while True:
            try:
                message = client.recv(1024).decode('ascii')

                if message == 'Private message':
                    requester_nickname = self.nicknames[client]
                    online_users = [nick for nick in self.nicknames.values() if nick != requester_nickname]
                    client.send(f'Online users: {online_users}\nWho do you want to send a private message to?'.encode('ascii'))
                    target = client.recv(1024).decode('ascii')

                    if target not in online_users:
                        client.send("NOT ONLINE".encode('ascii'))

                    else:
                        client.send("\nEnter the private message below: ".encode('ascii'))
                        message = client.recv(1024).decode('ascii')
                        self.send_private_message(nickname, target, message)
                        client.send("Private message sent successfully.".encode('ascii'))


                elif message == 'Exit':
                    self.handle_client_exit(client)
                    break

                else:
                    self.broadcast_message(nickname, message)

            except Exception as e:
                print(f'Error: {e}')
                break

    def send_private_message(self, sender, target, message):
        target_client = self.clients.get(target)
        if target_client:
            target_client.send(f'From {sender}: {message}'.encode('ascii'))
        else:
            print(f'User {target} is not online.')

    def broadcast_message(self, sender, message):
        channel = self.channels[sender]
        for client in self.clients.values():
            if self.channels[self.nicknames[client]] == channel:
                client.send(f'From {sender}: {message}'.encode('ascii'))

    def handle_client_exit(self, client):
        nickname = self.nicknames[client]
        del self.clients[nickname]
        del self.nicknames[client]
        print(f'[-] {nickname} left the chat...')
        client.send('EXIT'.encode('ascii'))
        client.close()

if __name__ == "__main__":
    server = ChatServer()
    server.start()
