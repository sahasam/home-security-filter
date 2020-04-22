#clientsocket.py
#Created by: Sahas Munamala
#Date: 4/16/2020
#Description: ClientSocket is a class that represents the image server
#             sending the image for processing
import socket

class ClientSocket :
    #Constructor for ClientSocket. Default values shown
    #Change BUFSIZE to increase Buffer Size
    def __init__ (self, host='127.0.0.1', port=1234, BUFSIZE=2048) :
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        self.BUFSIZE = BUFSIZE

    #send the size of the image to the server
    def sendSize(self, bits) :
        msg = "SIZE %s" % len(bits)
        self.socket.sendall(msg.encode())

        answer = self.socket.recv(self.BUFSIZE)

        if( answer.decode() == "20" ): # server successfully received image size
            print( "server received image size" )
            return True
        return False

    #send the actual data of the image to the server
    def sendImg(self, bits) :
        self.socket.sendall(bits)
        answer = self.socket.recv(self.BUFSIZE) # get response code
        if( answer.decode() == "22" ): # server successfully received image
            print( "SUCCESS: sent image to server" )
            return True
        elif( answer.decode() == "21" ): # server failed to receive image
            print( "FAILED: send image to server" )

    #main run loop for a ClientSocket Object
    def run(self, image) :
        try:
            myFile = open(image, 'rb') # open image for sending
            bits = myFile.read() #read file in bindary format
            if( self.sendSize(bits) ) :
                self.sendImg(bits)
            else :
                print( "Failed to send size" )
        finally:
            myFile.close()
            self.socket.close()

#testing script. To run: python serversocket.py
if( __name__ == "__main__" ):
    print( "Testing ClientSocket --- " )
    cs = ClientSocket()
    cs.run("../utils/images/nomanssky2.jpg")
    print( "closing test run" )
