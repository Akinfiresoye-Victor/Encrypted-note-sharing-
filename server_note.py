import socket
import select
import rsa

HOST_IP= socket.gethostbyname(socket.gethostname())
HOST_PORT= 1234
public_key, private_key= rsa.newkeys(1024)

server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()
print('Server is Running\n')
print('Waiting for connections....\n')


server_socket_list= [server_socket]
clients= {}

#A function that receives messages from clients
def receive_message(client_socket):
    
    try:
        note= client_socket.recv(1024)
        if not note:
            return False
        note= rsa.decrypt(note, private_key).decode('utf-8')
        if not len(note):
            return False
        if len(note) >= 1024:
            note= None
            if client_socket in clients:
                client_socket.send(rsa.encrypt("Note musn't be more than 1024 words".encode('utf-8'), clients[client_socket]['public_key']))
            else:
                print(f"Error: Client: {client_socket} not found")
        return note
    except rsa.DecryptionError:
        print(f"Decryption error from client: {client_socket}")
    except Exception as e:
        print(f"Error receiving message from {client_socket}: {e}")
        return False


while True:
    read_socket, _, exception_sockets= select.select(server_socket_list, [], server_socket_list)
    for pending_client in read_socket:
        if pending_client==server_socket:
            client_socket, client_address= server_socket.accept()
            client_socket.send(public_key.save_pkcs1("PEM"))
            public_partner_data=client_socket.recv(1024)
            try:
                public_partner= rsa.PublicKey.load_pkcs1(public_partner_data)
            except Exception as e:
                print(f"Error: invalid public key from {client_socket}")
                client_socket.close()
                continue
            
            client_username= receive_message(client_socket)
            if client_username is False:
                client_socket.close()
                continue

            
            server_socket_list.append(client_socket)
            clients[client_socket]= {'username': client_username, 'public_key': public_partner}
            print(f"Server accepted connection from {client_username}")
        
        else:
            note= receive_message(pending_client)
            if note is False:
                if pending_client in clients:
                    print(f"{clients[pending_client]['username']} disconnected from the server")
                    server_socket_list.remove(pending_client)
                    del clients[pending_client]
                continue

            elif note:
                if pending_client not in clients:
                    print(f"Error: Message receieved from unknow client {pending_client}")
                    continue
                client_info= clients[pending_client]
                print(f"Note received from {client_info['username']}: {note}")
                try:
                    pending_client.send(rsa.encrypt("Note sent successfully".encode('utf-8'), client_info['public_key']))
                except Exception as e:
                    print(f"Error sending response to {pending_client}: {e}")
                    if pending_client in server_socket_list:
                        server_socket_list.remove(pending_client)
                    if pending_client in clients:
                        del clients[pending_client]
    for pending_client in exception_sockets:
        if pending_client in clients:
            print(f"{clients[pending_client]['username']} disconnected")
            server_socket_list.remove(pending_client)
            del clients[pending_client]
