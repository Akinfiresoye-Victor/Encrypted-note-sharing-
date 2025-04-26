import socket


import rsa


DEST_IP= socket.gethostbyname(socket.gethostname())
DEST_PORT= 1234 
public_key, private_key= rsa.newkeys(1024)



username= input('Username ')

client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((DEST_IP, DEST_PORT))
server_public_key_data = client_socket.recv(1024)
server_public_key = rsa.PublicKey.load_pkcs1(server_public_key_data)
client_socket.send(public_key.save_pkcs1("PEM"))

print("Connected Successfully!! ")
print("To exit/disconnect from the server just enter 'quit'")


if len(username) >32:
    print("Username must not surpass 32 words")
    username= input('Username ')
username= username
username=username.encode('utf-8')

client_socket.send(rsa.encrypt(username, server_public_key))




print(f"Welcome {username} kindly enter the note you want to send, maximum of 1024 words ")



while True:
    note= input(f"{username}> ")

    if note == 'quit':
        print("Thanks for your time we would love to see you later...")
        break
    
    elif len(note) > 1024:
        print('Note musnt be more than 1024 characters')
        continue
    elif not note:
        print('Invalid note make sure the note isnt empty')
        continue  
    else:
        note= note.encode('utf-8')
        client_socket.send(rsa.encrypt(note, server_public_key))
        try:
            print(rsa.decrypt(client_socket.recv(1024), private_key).decode('utf-8'))
        except rsa.DecryptionError:
            print("Error: Decryption failed, there is an issue with the server decrypting your message")
            break