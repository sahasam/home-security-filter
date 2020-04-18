class Error(Exception) :
    """ Base class for exceptions in this program """
    pass

class FailedRecvSize (Error) :
    def __init__ (self, expression, message) :
        self.expression = expression
        self.message = message

class FailedRecvImg (Error) :
    def __init__ (self, expression, message) :
        self.expression = expression
        self.message = message

class SocketClosedUnexpectedly (Error) :
    def __init__ (self, expression, message) :
        self.expression = expression
        self.message = message
