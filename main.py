#main.py
#main program thread that controls the high-level operation of the program
#
#Author: Sahas Munamala
#Date: 04/19/2020

from queue import Queue
import time

from serversocket import ServerSocketThread
import odmodel

def Main() :
    #Create queue
    q = Queue()

    #Create serversocket thread
    ss = ServerSocketThread(q)
    ss.start()

    #load in tfmodel

    #main loop: whenever queue has something in it, read it and
    #put it in a queue
    while True :
        image = q.get()
        print( "new image in queue detected" )

        #create tfmodelthread and start it
        odm = odmodel.odmodel()
        (boxes, scores, classes, num) = odm.runimage(image)
        print("scores: ", str(classes))
    print( "Closing" )

if __name__ == "__main__" :
    Main()
