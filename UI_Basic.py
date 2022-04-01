from tkinter import *
import tkinter as tk

class Application(Frame):
    def __init__(self,parent,**kw):
        Frame.__init__(self,parent,**kw)
        self.actualQuestion = 0
        self.answers = {}
        # Create a String variable to store our status string
        self.stateVar = StringVar()
        self.stateVar.set("Questão 0")

        # Create a label to display the status
        self.label1 = Label(textvariable=self.stateVar)
        self.label1.grid()

        # Creating Input
        self.inputEntry = tk.Entry(bd=1)
        self.inputEntry.grid()
        # Calling on_change when you press the return key
        self.inputEntry.bind("<Return>", self.submit)

        # Create a button which will change the status
        self.button = Button(text="Press me", command=self.submit)
        self.button.grid()

        parent.geometry("300x100")  # You want the size of the app to be 500x500
        parent.resizable(0, 0)  # Don't allow resizing in the x or y direction

    def submit(self, e=None):
        """Called when the button is pressed or Pressed enter"""
        self.answers[self.actualQuestion] = self.inputEntry.get()
        self.actualQuestion += 1
        self.stateVar.set(f'Questão {self.actualQuestion}')
        print(self.answers)

if __name__ == '__main__':
    root = Tk()
    root.title("Sockets demonstration")
    app = Application(root)
    app.grid()
    root.mainloop()