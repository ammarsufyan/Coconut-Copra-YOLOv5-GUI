# import everything from tkinter module
from tkinter import *
from subprocess import Popen
from threading import Thread
import sys ,os

# create a tkinter window
root = Tk()

# Open window having dimension 150x100
root.geometry('180x90')
event = Event()

def start_program():
    thread = Thread(target=startApp, args=(event,))
    thread.start()

def startApp(event):
    global p
    p = Popen(['python', "C:/Users/PC-01/Documents/AI/test_serial.py"])
        #exec(open("C:/Users/PC-01/Documents/AI/test_serial.py").read())
        
def stop_program():
    Popen.terminate(p)
    os.system('cls')
    
#def exit_program():
#    Popen.terminate(p)
#    os.kill(SystemExit)
#def startApp(event):
    #while True:
        # p = Popen(['python', "C:/Users/PC-01/Documents/AI/test_serial.py"])
        #exec(open("C:/Users/PC-01/Documents/AI/test_serial.py").read())
        # if event.is_set():
            # p.kill()
            # break
#     event.set()
#     root.quit
#     sys.exit()

# Create a Button
Start = Button(root, text = 'Start', bd = '5', bg = 'chartreuse', command = start_program)
Start.place(x=70, y=10)

Stop = Button(root, text = 'Stop', bd = '5', bg = 'red', command = stop_program)
Stop.place(x=70, y=50)

#Exit = Button(root, text = 'Exit', bd = '5', command = exit_program)
#Exit.pack()

root.mainloop()