from socket import socket, AF_INET, SOCK_DGRAM
UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
UDPServerSocket.bind(('localhost', 9501))
count = 0
rodadas = 0
pontos = 0
clientes = {}
enderecos = []
print("Aguardando mensagens de clientes...")


while count < 1:
    mensagem_cliente = UDPServerSocket.recvfrom(1024)
    msg = str(mensagem_cliente[0].decode())  # ([0]mensagem,([0]IP, [1]PORTA))
    endereco = mensagem_cliente[1]
    print(f'\nO cliente {endereco} enviou: "{msg}" e ta participando')
    clientes[endereco[1]] = pontos
    enderecos.append(endereco)
    count += 1

while rodadas < 5:
    mensa = str(input("pergunta:"))
    mensacod = mensa.encode()
    for item in enderecos:
        UDPServerSocket.sendto(mensacod, item)
    resp = UDPServerSocket.recvfrom(1024)
    res = str(resp[0].decode())
    if res == 'OI':
        clientes[resp[1][1]] += 1
    elif res == "0":
        clientes[resp[1][1]] -= 1
    else:
        clientes[resp[1][1]] += 0
    rodadas += 1
print(clientes)

