from socket import socket, AF_INET, SOCK_DGRAM

UDPSocket = socket(AF_INET, SOCK_DGRAM)

print("Eu sou o cliente!")

mensagem = input("\nDigite uma mensagem p/ enviar: ")

mensagem_codificada = mensagem.encode()

UDPSocket.sendto(mensagem_codificada, ('localhost', 9500))
