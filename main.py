#main.py
#main program thread that controls the high-level operation of the program
#
#Author: Sahas Munamala
#Date: 04/19/2020

import threading
import queue
import time
import serversocket

max_model_threads = 2

class ServerSocketThread (threading.Thread) :
    """This class serves as the threading wrapper
    around the serversocket class. It extends
    threading.Thread and takes in the queue. As new
    clients connect to the server and send over images,
    they are put into the queue for processing by the
    tfmodel thread"""
    def __init__ (self, q) :
        threading.Thread.__init__(self)
        self.q = q

    def run(self) :
        ss = serversocket.ServerSocket()
        ss.run(self.q)

class tfmodelthread (threading.Thread) :
    """This class serves as the threading wrapper around
    the main processing of the program. It takes the path
    to the image and runs it through the tensorflow model
    """
    def __init__ (self, q, image) :
        threading.Thread.__init__(self)
        self.q = q
        self.image = image

    def run(self) :
        print("Processing %s" % self.image)
        time.sleep(3)
        print("Done processing %s" % self.image)

def Main() :
    #Create queue
    q = queue.Queue()

    #Create serversocket thread
    ss = ServerSocketThread(q)
    ss.start()

    #load in tfmodel

    #main loop: whenever queue has something in it, read it and
    #put it in a queue
    while True :
        print( "in main model thread" )
        image = q.get()

        #create tfmodelthread and start it
        t = tfmodelthread(q, image)
        t.start()

    print( "Closing" )

if __name__ == "__main__" :
    Main()
