#main.py
#main program thread that controls the high-level operation of the program
#
#Author: Sahas Munamala
#Date: 04/19/2020

from networking import serversocket
from queue import Queue
import odmodel
import logging

logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s : %(levelname)s:%(message)s')

def Main() :
    #Create queues

    #input_q holds filenames that point towards images to process
    input_q = Queue()
    #output_q holds socket objects in an order that matches input_q
    output_q = Queue()

    #Create serversocket thread
    ss = serversocket.ServerSocketThread(input_q, output_q)
    ss.start()

    #main loop: whenever queue has something in it, read it and
    #           send it to the odm
    while True :
        image = input_q.get()
        logging.info( "new image in queue detected" )

        #create tfmodelthread and start it
        odm = odmodel.odmodel()
        if ( odm.findPerson(image) ) :
            logging.info( "person in image has been found" )

        #with the given information, find out if a person is inside

    print( "Closing" )

if __name__ == "__main__" :
    Main()
