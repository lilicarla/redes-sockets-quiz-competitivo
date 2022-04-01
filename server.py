from socket import socket, AF_INET, SOCK_DGRAM
import time
import threading
import random

# 1 thread programada para encerrar o jogo (e o servidor) após as últimas mensagens terem sido enviadas (__closeServer)

# 1 thread para adicionar o jogador e, quando o limite de participantes for atingido,
# iniciar o jogo e enviar as perguntas (__setGame)

# ordem das ações da thread __setGame : adicionar jogador -> aguardar os outros -> 
# começar partida -> entrar no loop* de 5 rodadas de perguntas -> enviar a menagem final -> encerrar

# *ordem das ações dentro do loop de perguntas: limpar os campos com dados da pergunta anterior ->
# pegar a nova pergunta dentro das cinco que são escolhidas aleatoriamente antes do jogo começar -> enviar pergunta
# -> iniciar a rodada -> começar o "timeout" de 10s para receber respostas -> encerrar rodada ->
#  iniciar uma pausa -> virificar quem não respondeu e colocar a pontuação destes -> iniciar nova rodada


# 1 thread para receber as respostas e adicionar a pontuação dos que responderam (__recvAnswers) 
# durante os intervalos válidos

# a pontuação dos que não responderam é definida após o timeout dentro da thread __setGame

# ordem dos rounds: 0, -1, 1, -1, 2, -1, 3, -1, 4, -1
# o (-1) serve para definir uma pausa entre cada rodada (pergunta + timeout),
# que é importante para o usuário se preparar para a próxima pergunta

# uma das threads dos jogadores (self.aux) é escolhida como auxiliar para realizar algumas ações que 
# não podem ser repetidas por todas


class GameServer:
    def __init__(self, host : str, port):
        self.serverHost = host
        self.serverPort = port
        self.UDPServerSocket = None
        self.listen = True
        self.playersRanking = {}
        self.playersAddresses = {}
        self.questionsDict = {}
        self.gameStarted = False
        self.round = -1
        self.correctAnswer = False
        self.answered = []
        self.aux = None # endereço da thread auxiliar
        self.sentFinalMsg = False

    def setUpServer(self):
        self.UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
        self.UDPServerSocket.bind((self.serverHost, self.serverPort))  

    def __clearFields(self):
        self.answered.clear()
        self.correctAnswer = False

    def __closeServer(self):
        while self.sentFinalMsg == False:
            pass
        self.listen = False

        time.sleep(3)
        print(f"\n\n---> pontuação final do jogo:\n")
        #{nome: pontuacao}
        print(self.playersRanking)
        result_score = []
        #dicionary.values() -> retorna os scores de cada posição
        for i in self.playersRanking:
            name = i
            score = self.playersRanking[i]
            result_score.append((name, score))

        sorted_by_second = sorted(result_score, key=lambda tup: tup[1])
        for tupla in sorted_by_second:
            name = tupla[0]
            score = tupla[1]
            print(f'\n {name} - ' + f'{score}')
        print("\n\n encerrando em 10s")
        time.sleep(10)
        self.UDPServerSocket.close()

    def setQuestions(self):
        file = open(r"qa.txt", "r")
        indexes = []
        lines = file.readlines()
        aux = 0

        while len(indexes) < 5:
            index = random.randrange(0,20)
            if not index in indexes:
                indexes.append(index)

        file.close()

        for i in indexes:
            self.questionsDict[aux] = lines[i].strip()
            aux += 1
    
    def __recvAnswers(self, res : bytes, address):
        name = self.playersAddresses[address]
        index = self.round
        
        if self.round != -1:
            # check answer
            self.answered.append(address)
            line = self.questionsDict[index]
            w = line.strip("(")
            z = w.strip(")")
            qa2 = z.split(",")
            correctAnswer : str = qa2[1]
            playerAnswer = res.decode()

            # set points
            if correctAnswer == playerAnswer:
                self.correctAnswer = True
                self.playersRanking[name] += 25
            else:
                self.playersRanking[name] -= 5

            score = self.playersRanking[name]
            print("\n# " + name + " respondeu: " + playerAnswer + " | nova pontuação --> " + f'{score}')

    def __getNextQuestion(self, index) -> str:

        # get next question
        nextLine = self.questionsDict[index]
        x = nextLine.strip("(")
        y = x.strip(")")
        qa1 = y.split(",")
        q : str = qa1[0]

        return q

    def __sendGameStatus(self,address, accepted : bool):

        resDenied = "DENIED"
        resAccepted = "OK"

        if accepted:
            self.UDPServerSocket.sendto(resAccepted.encode(), address)
        else:
            self.UDPServerSocket.sendto(resDenied.encode(), address)
    
    def __sendQuestion(self, address, index):

        # clear last question fields
        self.__clearFields()

        # get next question
        newQuestion = self.__getNextQuestion(index)

        # send question
        self.UDPServerSocket.sendto(newQuestion.encode(), address)

        if self.aux == address:
            # print current question
            print("\n---> Pergunta " + f"{index + 1}" + " enviada")
            # set round
            self.round = index
        
    def __setTimeout(self, address, index : int):

        # duration of rounds
        i=0
        while i < 10 and self.correctAnswer == False:
            time.sleep(1)
            i += 1

        # draw a line to separate rounds
        line = "BR"
        self.UDPServerSocket.sendto(line.encode(), address)

        # set rounds
        if self.aux == address:
            self.round = -1
        
        # in case the player has not sent a reply
        if address not in self.answered:
            name = self.playersAddresses[address]
            self.playersRanking[name] -= 1
            score = self.playersRanking[name]
            print("\n# "+ f'{name}' + " não respondeu | nova pontuação --> " + f'{score}')
        
        # pause between rounds (except the last one)
        if index < 4:
            time.sleep(5)

    def __setGame(self, res : bytes, address):

        # register a player
        if address not in self.playersAddresses:
            
            if not self.gameStarted:

                # add new player
                if len(self.playersAddresses) < 5: 
                    playerName = res.decode()
                    # add to ranking {name: score}
                    self.playersRanking[playerName] = 0
                    # add to address dictionary {[address]: name}
                    self.playersAddresses[address] = playerName
                    print("\n---> "+playerName + " entrou no jogo")
                    # send confirmation message
                    self.__sendGameStatus(address = address, accepted=True)

                    # start game when the last player joins
                    if len(self.playersAddresses) == 5:
                        self.gameStarted = True
                        self.aux = address # choose the last player's thread as a helper for some commands
                        print("\n________ começando ________")

                    if not self.gameStarted:
                        print("\n Aguardando mais jogadores...")
                        if len(self.playersAddresses) == 1:
                            time.sleep(90)
                            self.gameStarted = True
                            self.aux = address
                    # wait for new players
                    while not self.gameStarted:
                        pass
                    
                    # start game rounds
                    for i in range(0,5):

                        self.__sendQuestion(address=address, index=i)
                        self.__setTimeout(address=address, index=i)

                    # send final message
                    finalMsg = "end"
                    self.UDPServerSocket.sendto(finalMsg.encode(), address)
                    if self.sentFinalMsg == False:
                        self.sentFinalMsg = True

                # limit reached
                else:
                    self.__sendGameStatus(address=address, accepted=False)

    def receiveData(self):

        # start game server
        print('\n\n INICIO')
        print('\n aguardando jogadores...')
        
        # to configure when the game ends
        threading.Thread(target=self.__closeServer).start()

        while self.listen:
            try:   
                # receive messages from clients
                clientM, clientA = self.UDPServerSocket.recvfrom(1024)

                # message from a non-player client (during a match that has already started)
                if self.gameStarted and clientA not in self.playersAddresses:
                    self.__sendGameStatus(address=clientA, accepted=False)

                # set up the game
                else:
                    try:
                        threading.Thread(target=self.__setGame, args=[clientM, clientA]).start()

                        # receive answers from registered players
                        if clientA in self.playersAddresses and self.listen:
                            threading.Thread(target=self.__recvAnswers, args=[clientM, clientA]).start()

                    except OSError as threadingError:
                        print('\nerro THREAD ' + f'{threadingError}')
                        self.listen = False

            except OSError as error:
                print("\n_______FIM_______") 
                
def main():
    match = GameServer('localhost', 9500)
    match.setQuestions()

if __name__ == '__main__':
    main()