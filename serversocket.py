#serversocket.py
#Server socket handler for camFilter. Receives images from remove server,
#sends the image to the main file, then sends back whether a person
#was detected or not
#
#Sahas Munamala
#4/15/2020
import socket
from error import *


class ServerSocket :


    def __init__ (self, host='127.0.0.1', port=1234, max_connections=10) :
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ss.bind((host,port))
        self.ss.listen(max_connections)

        self.basename = "./utils/images/image"
        self.imgcount = 0

    def close(self) :
        self.ss.close()

    def run(self) :
        BUFSIZE = 2048
        imgcount = 0
        basename = "./utils/images"
        cl_socket, addr = self.ss.accept()

        try:
            myFile = open("%s%d.jpg" % (basename, imgcount), 'wb')

            data = cl_socket.recv(BUFSIZE)
            msg = data.decode()
            size=0
            if( msg.startswith("SIZE") ):
                print( 'Received size marker' )
                size = int(msg.split()[1])
                cl_socket.send("20".encode())
            else:
                print( 'failed to receive size' )
                cl_socket.send("19".encode())
                raise FailedRecvSize('oops', 'wont happen again')

            totaldata = 0
            while True :
                data = cl_socket.recv(BUFSIZE)

                if data :
                    #print( 'receiving image' )
                    myFile.write(data)

                    totaldata += len(data)
                else :
                    print('socket at %d is closing' % addr)
                    myFile.close()
                    break

                if( totaldata>=size ):
                    cl_socket.send("21".encode())
                    break


            print( 'done recv image' )
        finally:
            myFile.close()
            cl_socket.close()

if( __name__ == "__main__" ):
    print( "Testing server socket --- " )
    ss = ServerSocket()
    ss.run()
    print( "Successfully reached end. Closing" )



