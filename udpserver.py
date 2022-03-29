from socket import socket, AF_INET, SOCK_DGRAM

UDPServerSocket = socket(AF_INET, SOCK_DGRAM)

UDPServerSocket.bind(('localhost', 9500))

print("Aguardando mensagens de clientes...")

while True:
    mensagem_cliente = UDPServerSocket.recvfrom(1024)
    msg = str(mensagem_cliente[0].decode())  # ([0]mensagem,([0]IP, [1]PORTA))
    endereco = mensagem_cliente[1]
    print(f'\nO cliente {endereco} enviou: "{msg}"')
