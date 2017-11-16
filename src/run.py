from yowsup.stacks import  YowStackBuilder
from layer import EchoLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.env import YowsupEnv

credentials = ("919819057179", "/A/MgwPTiwqeodyRHa6hFC7Ug+Q=") # replace with your phone and password

if __name__==  "__main__":
    stackBuilder = YowStackBuilder()

    stack = stackBuilder\
        .pushDefaultLayers(True)\
        .push(EchoLayer)\
        .build()

    stack.setCredentials(credentials)
    print("Credentials Set")
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal
    stack.loop() #this is the program mainloop
