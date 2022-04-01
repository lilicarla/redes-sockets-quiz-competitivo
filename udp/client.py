from socket import socket, AF_INET, SOCK_DGRAM
import threading
import time

# 1 thread (__fromServer) para receber mensagens do servidor, decodificá-las, exibir no terminal
# e definir as ações atribuídas a cada tipo de mensagem

# 1 thread (__sendAnswer) para responder cada pergunta
# o usúário deve sempre "destravar" o input, seja mandando uma reposta 
# ou digitando qualquer valor + ENTER durante o período de pausa entre as rodadas

# existe um timeout que encerra o socket após um tempo

class SocketClient:
    def __init__(self, initHost, initPort):
        self.host = initHost
        self.port = initPort
        self.UDPClientSocket = None
        self.listen = True
        self.qNumber = 0 # questions
        self.sentAnswr = False

    def setSocket(self):
        self.UDPClientSocket = socket(AF_INET, SOCK_DGRAM)

    def __sendAnswer(self):
        self.sentAnswr = False
        # send messages to server
        answer = str(input("\n>>>"))
        resp = answer.encode()
        self.sentAnswr = True
        if self.listen:
            try:
                self.UDPClientSocket.sendto(resp, ('localhost', 9500)) #localhost 9500
            except OSError as error:
                print(f"\nERRO: '{error}'")
                self.listen = False
                print("\n\n______FIM______")
                self.UDPClientSocket.close()
        else:
            print("\nvocê foi desconectado")

    def __setActions(self, serverMsg : bytes):

        sMsg = serverMsg.decode()

        # request denied
        if sMsg == 'DENIED': 
            self.listen = False
            self.UDPClientSocket.close()

        # end of the game
        elif sMsg == 'end':
            self.listen = False
            time.sleep(5)
            self.UDPClientSocket.close()

        # divider
        elif sMsg == 'BR':
            pass
        
        # request accepted
        elif sMsg == 'OK':
            pass

        # questions
        else:
            self.qNumber += 1
            if self.qNumber == 1:
                threading.Thread(target=self.__sendAnswer).start()
            else:
                while self.sentAnswr == False:
                    pass

                threading.Thread(target=self.__sendAnswer).start()

    def __decodeServerMsg(self, serverMsg : bytes) -> str:
        message = serverMsg.decode()

        # request accepted
        if message == 'OK':
            return "\n Aguarde a partida começar"

        # request denied
        elif message == 'DENIED': 
            return "\n Uma partida já está acontecendo, tente novamente depois"
            
        # divider
        elif message == 'BR':
            if self.qNumber == 5:
                return ""
            else:
                return "\n _______________________________________________\n\n # aguarde próxima pergunta #"

        # end of the game
        elif message == 'end': 
            return "\n\n______FIM______"

        # questions
        else:
            return f"\n {message}"
            

    def __fromServer(self):

        self.UDPClientSocket.settimeout(180)
        while self.listen:
            try:
                serverData = self.UDPClientSocket.recvfrom(1024)
                serverMsg = serverData[0]
                self.started = True
                
                decodedMsg = self.__decodeServerMsg(serverMsg)
                print(decodedMsg)
                self.__setActions(serverMsg)

            except OSError as error:
                print('\ntimeout')
                self.listen = False
                self.UDPClientSocket.close()

    def requestAccess(self):

        # start client
        print("\n_______ QUIZ _______\n")

        # instructions
        print("\n ### INSTRUÇÕES ###")
        print("\n\n RESPOSTA CORRETA: 25 PONTOS")
        print("\n RESPOSTA ERRADA: -5 PONTOS")
        print("\n SEM RESPOSTA: -1 PONTOS")
        print("\n\n 1. todas as respostas devem conter apenas letras minúsculas ou números")
        print("\n 2. uma rodada se encerra após 10 segundos ou caso algum jogador acerte a resposta")
        print("\n 3. se a rodada terminar e você ainda estiver respondendo,\n digite mais algum caractere, pressione ENTER e aguarde a próxima pergunta")
        print("\n 4. se não souber a resposta, aguarde a rodada terminar,\n digite qualquer valor, pressione ENTER e aguarde a próxima pergunta")
        time.sleep(3)
        confirmation = str(input("\n OK? : "))

        if confirmation == 'ok':
            # send first message to server
            clientName = str(input("\n Digite seu nome: "))
            initMsg = clientName.encode()
            self.UDPClientSocket.sendto(initMsg, (self.host, self.port)) #localhost 9500
            
            # receive messages from server
            threading.Thread(target=self.__fromServer).start()
        else:
            print("\n\n______FIM______")
            self.UDPClientSocket.close()

def main():
    game1 = SocketClient('localhost', 9500)
    game1.setSocket()
    game1.requestAccess()

if __name__ == '__main__':
    main()