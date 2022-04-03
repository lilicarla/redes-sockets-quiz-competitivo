from tkinter import *
import tkinter as tk
from socket import socket, AF_INET, SOCK_DGRAM
import threading
import time

class Application(Frame):
    def __init__(self, parent, **kw):
        Frame.__init__(self, parent, **kw)
        self.actualQuestion = -2
        self.lastAnswer = ''
        self.host = 'localhost'
        self.port = 9500
        self.UDPClientSocket = None
        self.listen = True
        self.sentAnswer = False
        self.root = parent
        # Create a String variable to store our status string
        self.stateVar = StringVar()
        self.stateVar.set("OK?")

        # Create a label to display the status
        self.label1 = Label(textvariable=self.stateVar)
        self.label1.grid()

        # Creating Input
        self.inputEntry = tk.Entry(bd=1)
        self.inputEntry.grid()
        # Calling on_change when you press the return key
        self.inputEntry.bind("<Return>", self.submit)

        # Create a button which will change the status
        self.button = Button(text="enviar", command=self.submit)
        self.button.grid()

        parent.geometry("300x100")  # You want the size of the app to be 500x500
        parent.resizable(0, 0)  # Don't allow resizing in the x or y direction

        self.setSocket()

    def submit(self, e=None):
        """Called when the button is pressed or Pressed enter"""
        self.inputEntry.config(state="disabled")
        self.button.config(state="disabled")
        self.sentAnswer = False
        answer = self.inputEntry.get()
        self.lastAnswer = answer
        response = answer.encode()
        self.sentAnswer = True

        if self.actualQuestion == -2:
            self.requestAccess()
        else:
            if self.listen:
                try:
                    self.UDPClientSocket.sendto(response, ('localhost', 9500))
                except OSError as error:
                    print(f"\nERRO: '{error}'")
                    self.listen = False
                    print("\n\n______FIM______")
                    self.UDPClientSocket.close()
                    self.root.destroy()
            else:
                print("\nvoce foi desconectado")
                #fechar a janela aqui
                self.root.destroy()


    def showNewQuestion(self, title):
        self.inputEntry.delete(0, 'end')
        self.actualQuestion += 1
        self.stateVar.set(title)
        self.inputEntry.config(state="normal")
        self.button.config(state="normal")

    def changeTitle(self, title):
        self.stateVar.set(title)

    def setSocket(self):
        self.UDPClientSocket = socket(AF_INET, SOCK_DGRAM)

    def __setActions(self, serverMsg: bytes):
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

        # wait next question
        elif sMsg == 'wait':
            pass

        # questions
        else:
            if self.actualQuestion == 1:
                threading.Thread().start()
            else:
                while self.sentAnswer == False:
                    pass
                threading.Thread().start()

    def __decodeServerMsg(self, serverMsg: bytes) -> str:
        message = serverMsg.decode()

        # request accepted
        if message == 'OK':
            self.changeTitle("Enviado! Aguarde a partida começar")

        # request denied
        elif message == 'DENIED':
            self.changeTitle("Uma partida já está acontecendo, tente novamente depois")

        # divider
        elif message == 'BR':
            if self.actualQuestion == 5:
                self.changeTitle("")
            else:
                self.changeTitle("# aguarde próxima pergunta #")
                self.inputEntry.config(state="disabled")
                self.button.config(state="disabled")

        # end of the game
        elif message == 'end':
            self.changeTitle("______FIM______")

        # questions
        else:
            self.showNewQuestion(message)

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

    def sendName(self):
        initMsg = self.lastAnswer.encode()
        print('teste')
        print(self.lastAnswer)
        self.UDPClientSocket.sendto(initMsg, (self.host, self.port))
        threading.Thread(target=self.__fromServer).start()


    def requestAccess(self):
        confirmation = str(self.lastAnswer)

        if confirmation.lower() == 'ok':
            self.showNewQuestion("Seu nome será enviado em 10 segundos, digite aqui:")
            #giving 5sec to input a name or the name will be OK
            self.inputEntry.after(10000, self.sendName)
        else:
            self.UDPClientSocket.close()
            self.root.destroy()

if __name__ == '__main__':
    root = Tk()
    root.title("Sockets demonstration")
    app = Application(root)
    app.grid()
    root.mainloop()