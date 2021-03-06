import socket

import select

HEADER_LENGTH = 10

IP = "192.168.1.11"
PORT = 8000

server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #Removing the pesky "Address already in use error"

server_socket.bind((IP,PORT))

server_socket.listen()

sockets_list = [server_socket]
clients = {}

print(f"Listening for connections on {IP} on port {PORT}...")

#Recieving messages

def receive_msg(client_socket):

	try:
		message_header = client_socket.recv(HEADER_LENGTH) #Locating the header

		#For when "socket.close()" is issued
		if not len(message_header):
			return False

		message_length = int(message_header.decode("utf-8").strip()) #Decoding the Header's length

		return {"header": message_header, "data": client_socket.recv(message_length)} #The Header and the actual Data


	except:
		#For when something goes wrong (empty message or client cutting out abruptly)
		return False

while True:
	read_sockets,_,exception_sockets = select.select(sockets_list, [], sockets_list) # syntax = select.select(READ_LIST, WRITE_LIST, ERROR_LIST)

	for notified_socket in read_sockets:
		if notified_socket == server_socket:
			#For when the user (client) first establishes the connection
			client_socket, client_address = server_socket.accept()
			user = receive_msg(client_socket)

			if user is False:
				continue

			#Adding the client to the list of users' list
			sockets_list.append(client_socket)
			clients[client_socket] = user
			print("New connection accepted from {}:{}, username:{}".format(*client_address, user["data"].decode("utf-8")))
			new_user_info = user["data"]
			new_user_message = "/%&? has entered the dungeon./%&?".encode("utf-8")
			new_user_message_header = f"{len(new_user_message):<{HEADER_LENGTH}}".encode("utf-8")
			new_user_info_header = f"{len(new_user_info):<{HEADER_LENGTH}}".encode("utf-8")
			for client_socket in clients:
				client_socket.send(new_user_info_header + new_user_info + new_user_message_header + new_user_message)


		else:
			#For the message
			message = receive_msg(notified_socket)
			
			#For when the client disconnects
			if message is False:
				print("Closed connection from: {}".format(clients[notified_socket]["data"].decode("utf-8")))
				user_left_info = clients[notified_socket]["data"]
				user_left_message = "/%&? has left the dungeon./%&?".encode("utf-8")
				user_left_message_header = f'{len(user_left_message):<{HEADER_LENGTH}}'.encode("utf-8")
				user_left_info_header = f'{len(user_left_info):<{HEADER_LENGTH}}'.encode("utf-8")
				for client_socket in clients:
					if client_socket != notified_socket:
						client_socket.send(user_left_info_header + user_left_info + user_left_message_header + user_left_message)
				
				sockets_list.remove(notified_socket)
				del clients[notified_socket]

				continue



			#Now for recieving the message
			user = clients[notified_socket]
			print(f'Received message from {user["data"].decode("utf-8")} : {message["data"].decode("utf-8")}')
			#print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')


			#Broadcasting the message to all the clients
			for client_socket in clients:
				#But not the the sender
				if client_socket != notified_socket:
					client_socket.send(user["header"] + user["data"] + message["header"] + message["data"])

	#Exception Handling
	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket) #Removing the socket from the "Notified Sockets"
		del clients[notified_socket] #Removing the Client from the list of users