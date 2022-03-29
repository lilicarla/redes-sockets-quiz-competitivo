from socket import socket, AF_INET, SOCK_DGRAM
UDPSocket = socket(AF_INET, SOCK_DGRAM)

print("Eu sou o cliente!")
rodadas = 0
mensagem = input("\nDigite uma mensagem p/ enviar: ")

mensagem_codificada = mensagem.encode()

UDPSocket.sendto(mensagem_codificada, ('localhost', 9501))
pergunta = ""
UDPSocket.gettim
while rodadas < 5:
    perguntaser = UDPSocket.recvfrom(1024)
    pergunta = str(perguntaser[0].decode())
    print(pergunta)
    UDPSocket.settimeout(5)
    try:
        res = input("responde:")
        rescod = res.encode()
        UDPSocket.sendto(rescod, ('localhost', 9501))
    except:
        nada = "0"
        nadacod = nada.encode()
        UDPSocket.sendto(nadacod, ('localhost', 9501))
    rodadas += 1
