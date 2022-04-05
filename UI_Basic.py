from tkinter import *
from tkinter import ttk
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
        self.label1 = ttk.Label(parent,
                            padding=(10,20),
                            width= 100,
                            textvariable=self.stateVar,
                            font=('Arial', 10),
                            justify='center',
                            anchor=CENTER)
        self.label1.pack()

        # Creating Input
        self.inputEntry = ttk.Entry(parent,
                                    width=35,
                                    font=('Arial', 10))
        self.inputEntry.pack()

        # Calling on_change when you press the return key
        self.inputEntry.bind("<Return>", self.submit)

        # Create a button which will change the status
        self.button = ttk.Button(parent,
                            text="enviar",
                            padding=3,
                            width=10,
                            command=self.submit)
        self.button.pack()

        # place widgets
        self.label1.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.inputEntry.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.button.place(relx=0.5, rely=0.7, anchor=CENTER) 
        
        self.setStyle()
        parent.resizable(1, 0)  # Don't allow resizing in the y direction

        self.setSocket()

    def setStyle(self):
        width = 650
        heigh = 250
        screenSizeY = self.winfo_screenheight()
        screenSizeX = self.winfo_screenwidth()
        posx = screenSizeX / 2 - width /2
        posy = screenSizeY / 2 - heigh /2
        self.root.geometry("%dx%d+%d+%d" %(width, heigh, posx, posy))

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
        self.actualQuestion += 1
        self.stateVar.set(title)
        self.inputEntry.config(state="normal")
        self.button.config(state="normal")
        self.inputEntry.delete(0, tk.END)

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
            if self.actualQuestion == 4:
                self.changeTitle('PONTUAÇÃO FINAL: '+ message)
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
    root.mainloop()