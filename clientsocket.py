#clientsocket.py
#Created by: Sahas Munamala
#Date: 4/16/2020
import socket

class ClientSocket :


    def __init__ (self, cl_socket, addr) :
        self.socket = cl_socket


    def __init__ (self, host='127.0.0.1', port=1234) :
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))

    def run(self, image) :
        BUFSIZE = 2048
        try:
            myFile = open(image, 'rb')
            bits = myFile.read()

            msg = "SIZE %s" % len(bits)
            self.socket.sendall(msg.encode())

            answer = self.socket.recv(BUFSIZE)
            print( "server response: %s" % answer.decode() )

            if( answer.decode() == "20" ):
                #server has received imagesize
                self.socket.sendall(bits)

                answer = self.socket.recv(BUFSIZE)

                if( answer.decode() == "21" ):
                    print( "successfully sent image to server" )
        finally:
            myFile.close()
            self.socket.close()

if( __name__ == "__main__" ):
    print( "Testing ClientSocket --- " )
    cs = ClientSocket()
    cs.run("./utils/images/nomanssky2.jpg")
    print( "closing test run" )


