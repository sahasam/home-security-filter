#serversocket.py
#Server socket handler for camFilter. Receives images from remove server,
#sends the image to the main file, then sends back whether a person
#was detected or not
#
#Sahas Munamala
#4/15/2020
import socket
import threading
from error import *


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
        ss = ServerSocket()
        ss.run(self.q)

#This class runs the serversocket logic. It spawns new ServerClientSocket which 
#accept images from incoming connections
class ServerSocket :
    #basename: path of image to save
    #imgcount: number of image to save (prevents duplicate file names)
    def __init__ (self, host='127.0.0.1', port=1234, max_connections=10) :
        self.host = host
        self.port = port
        try:
            self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ss.bind((host,port))
            self.ss.listen(max_connections)
        except socket.error as err :
            print( "failed to create server socket" )

        self.basename = "./utils/images/image"
        self.imgcount = 0

    def close(self) :
        self.ss.close()

    #main run logic for a ServerSocket object
    def run(self, q) :
        while True:
            cl_socket, addr = self.ss.accept()
            imagepath = "%s%d.jpg" % (self.basename, self.imgcount)
            scs = ServerClientSocket(cl_socket, imagepath)
            self.imgcount = self.imgcount + 1
            threading.Thread(target = self.runclient(cl_socket, addr, scs, q))

    def runclient(self, cl_socket, addr, scs, q) :
        try:
            scs.run(q)
        finally:
            scs.close()

#This class reads image data from socket and saves it to a file before
#closing
class ServerClientSocket :

    #cl_socket: socket object that ServerClientSocket controls
    #imgpath: full path of file to save image to 
    def __init__ (self, cl_socket, imgpath) :
        self.cl_socket = cl_socket
        self.imgpath = imgpath

    def close(self) :
        self.cl_socket.close()

    #receive the image size from the socket
    def recvImgSize(self) :
        BUFSIZE = 2048
        data = self.cl_socket.recv(BUFSIZE)
        msg = data.decode()
        if( msg.startswith("SIZE") ):
            print( 'received size marker' )
            size = int(msg.split()[1])
            self.cl_socket.send("20".encode())
            return size
        else :
            print( 'failed to receive size marker' )
            self.cl_socket.send("19".encode())
            self.cl_socket.close()
            raise FailedRecvSize('oops', 'something went wrong')

        return -1

    #receive the image data from the socket
    def recvImg(self, myFile, size) :
        BUFSIZE = 2048
        totaldata = 0
        while True :
            data = self.cl_socket.recv(BUFSIZE)
            if data :
                #print( 'receiving image' )
                myFile.write(data)
                totaldata += len(data)
            else :
                self.cl_socket.send("21".encode())
                myFile.close()
                break
            if( totaldata>=size ):
                self.cl_socket.send("22".encode())
        print( 'done recv image' )

    #main logic loop of a ServerClientSocket
    def run(self, q) :
        myFile = open(self.imgpath, 'wb')
        try:
            size = self.recvImgSize()
            self.recvImg(myFile, size)
            q.put(self.imgpath)
        except FailedRecvSize as err :
            print( "Failed to receive size from socket. Check connection" )
        finally :
            myFile.close()

    def close(self) :
        self.cl_socket.close()


if( __name__ == "__main__" ):
    import queue
    print( "Testing server socket --- " )
    q = queue.Queue()
    ss = ServerSocketThread(q)
    ss.start()
    print( "Successfully reached end. Closing" )

