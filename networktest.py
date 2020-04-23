import networking.serversocket as nss

if __name__ == "__main__" :
    cs = nss.ClientSocket()
    cs.run("./utils/testimage.jpg")
    print( "finished test run" )
