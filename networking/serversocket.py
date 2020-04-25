#serversocket.py
#Server socket handler for camFilter. Receives images from remove server,
#sends the image to the main file, then sends back whether a person
#was detected or not
#
#Sahas Munamala
#4/15/2020
import socket
import threading
import time

BUFSIZE=2048

class ServerSocketThread (threading.Thread) :
    """This class serves as the threading wrapper
    around the serversocket class. It extends
    threading.Thread and takes in the queue. As new
    clients connect to the server and send over images,
    they are put into the queue for processing by the
    tfmodel thread"""
    def __init__ (self, input_q, output_q) :
        threading.Thread.__init__(self)
        self.input_q = input_q
        self.output_q = output_q


    def run(self) :
        ss = ServerSocket()
        ss.run(self.input_q, self.output_q)


#This class runs the serversocket logic. It spawns new ServerClientSocket which 
#accept images from incoming connections
class ServerSocket :
    """Handles the process of accepting connections
    and spawning threads to receive images from clients
    """
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

        self.lock = threading.Lock()

    def close(self) :
        self.ss.close()

    def run(self, input_q, output_q) :
        while True:
            cl_socket, addr = self.ss.accept()
            imagepath = "%s%d.jpg" % (self.basename, self.imgcount)
            scs = ServerCommSocket(cl_socket, imagepath)
            self.imgcount = self.imgcount + 1
            threading.Thread(target = self.runclient(scs, input_q, output_q))

    def runclient(self, scs, input_q, output_q) :
        try:
            scs.run(input_q, output_q, self.lock)
        finally:
            scs.close()


class ClientSocket :
    def __init__ ( self, host='127.0.0.1', port=1234 ) :
        self.host = host
        self.port = port
        try:
            self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cs.connect((host,port))
        except socket.error as err :
            print( "could not open socket" )

    def run (self, imgpath) :
        ccs = ClientCommSocket(self.cs, imgpath)
        ccs.run()

#This class reads image data from socket and saves it to a file before
#closing
class CommSocket :
    """This class handles low level implementation of socket
    communication. This class is not intended to be used directly,
    but gives classes that inherit it functions to send and recv images
    """
    def __init__ (self, cl_socket) :
        """
        cl_socket: socket where commmunication is managed
        """
        self.cl_socket = cl_socket

    def _recvImgSize(self) :
        """Receive the size of the image from the socket.
        Assumes that the other side is trying to send image size.

        Codes:
        20: Successfully received image size
        19: Failed to recieve image size

        Returns:
        size if successful, or -1 if failed
        """
        data = self.cl_socket.recv(BUFSIZE)
        msg = data.decode()
        if( msg.startswith("SIZE") ):
            size = int(msg.split()[1])
            print( "collected size: ", size)
            self.cl_socket.send("20".encode())
            print( "sent 20" )
            return size
        else :
            self.cl_socket.send("19".encode())
            self.cl_socket.close()
            raise FailedRecvSize('oops', 'something went wrong')
        return -1

    def _recvImgData(self, myFile, size) :
        """Receives actual image data from the socket
        Assumes the other side is trying to send image data.

        Parameters:
        myFile  : opened output file to write image data to
        size    : number of bits to receive

        Codes:
        21  : socket closed before full image could be sent
        22  : received full image from socket successfully
        """
        totaldata = 0
        while True :
            data = self.cl_socket.recv(size)
            #print (data)
            if data :
                myFile.write(data)
                totaldata += len(data)
            else :
                myFile.close()
                break
            print( totaldata, "/", size )
            if( totaldata >= size ) :#>=size ):
                self.cl_socket.send("22".encode())
                break
        print( 'done recv image' )

    def _sendSize(self, bits) :
        """Send size of image to other socket.
        Assumes the other side is ready to receive image size

        Parameters:
        bits    : raw image data that is measured and sent

        Returns:
        True    : image size sent successfully
        False   : image size not sent successfully
        """
        msg = "SIZE %s" % len(bits)
        print( msg )
        self.cl_socket.sendall(msg.encode())
        answer = self.cl_socket.recv(BUFSIZE)

        if( answer.decode() == "20" ): # server successfully received image size
            print( "client received image size" )
            return True
        return False

    def _sendImgData(self, bits) :
        """Send image data to other socket
        Assumes that other socket is ready to receive.

        Parameters:
        bits    : raw image data that is measured and sent

        Returns :
        True: destination socket received image data
        False: image data not sent successfully
        """
        self.cl_socket.sendall(bits)
        answer = self.cl_socket.recv(BUFSIZE) # get response code
        if( answer.decode() == "22" ): # server successfully received image
            print( "SUCCESS: sent image to server" )
            print( "testing" )
            return True
        elif( answer.decode() == "21" ): # server failed to receive image
            print( "FAILED: send image to server" )
        return False

    def _send_if_person_detected(self, message) :
        """Send a string that determines whether or not a
        person was found in the image

        Parameters:
        message:    string value that indicates if a person was found or not
        """
        self.cl_socket.sendall(message.encode())
        answer = self.cl_socket.recv(BUFSIZE)
        if( answer.decode() == "24" ):
            print( "SUCCESS: sent %s to client" % message )
            return True
        else :
            print( "FAILED: could not send %s to client" % message )
        return False

    def _recv_if_person_detected(self) :
        """Recv a string that determines whether or not a
        person was found in the image
        """
        message = self.cl_socket.recv(BUFSIZE)
        if( message.decode() == "True" ):
            print( "Server found person in image" % message )
            return True
        else :
            print( "Server did not find person in image" % message )
        return False

    def close(self) :
        """Close socket for further use"""
        self.cl_socket.close()


class ServerCommSocket (CommSocket) :
    """This class handles communication from the server's side
    of the program. It receives images from the client for
    processing and sends back images that actually contain people.
    """
    def __init__ (self, cl_socket, imgpath) :
        """__init__ for ServerCommSocket

        Parameters:
        cl_socket : socket that communicates with client
        imgpath   : path to save the image received to
        """
        super().__init__(cl_socket)
        self.imgpath = imgpath

    def run (self, input_q, output_q, lock) :
        """Method that handles run logic for Server Socket

        Parameters:
        input_q: queue to place image after receiving for further processing
        """
        myFile = open(self.imgpath, 'wb')
        try:
            size = self._recvImgSize()
            self._recvImgData(myFile, size)
            print( "putting %s in input_q" % self.imgpath )
            input_q.put(self.imgpath)
            print( "imgpath: ", self.imgpath )

            lock.acquire()
            print( "Lock Acquired" )
            contains_person = output_q.get()
            if contains_person is True :
                self._send_if_person_detected('True')
            lock.release()
            print( "Lock Released" )

            #TODO find way to delete iamge

        finally:
            myFile.close()
            self.close()
        print( "Finished Serverside Socket Communication" )


class ClientCommSocket (CommSocket) :
    """Handles communication from the client's side of the program.
    It sends images to the server for processing and waits to see if
    the server found a person in the image"
    """
    def __init__ (self, cl_socket, imgpath) :
        """__init__ for ClientCommSocket

        Parameters:
        cl_socket : socket that communicates with server
        imgpath   : filesystem location of image to be sent
        """
        super().__init__(cl_socket)
        self.cl_socket = cl_socket
        self.imgpath = imgpath

    def run (self) :
        """ Run method that handles communication from the client's
        side of the program. It sends images to the server and waits
        for the server to say if it finds a person or not"""
        try:
            myFile = open(self.imgpath, 'rb')
            bits = myFile.read()
            if( self._sendSize(bits) ):
                self._sendImgData(bits)
                print( "made it to the if statement" )
                if self._recv_if_person_detected() is True :
                    print( "person has been found in the iamge" )
            else :
                print( "failed to send size" )
        finally :
            self.close()
        print( "Finished Clientside Socket Communication" )


if( __name__ == "__main__" ):
    from queue import Queue
    print( "Testing server socket --- " )
    input_q = Queue()
    output_q = Queue()
    ss = ServerSocketThread(input_q, output_q)
    ss.start()
    while True :
        ext = input_q.get()
        print( "input queue has been populated with", str(ext) )
    print( "Successfully reached end. Closing" )
