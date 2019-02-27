from Workspace import Workspace
from DeclarativeMemory import DeclarativeMemory
from pubsub import pub
import pandas as pd

class PerceptualAssociativeMemory:

    def __init__(self, user, csm):

        # recebe usuario do ambiente
        self.user = user

        self.csm = csm

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.dm = DeclarativeMemory(self.user, self.csm)
        self.user_data = self.dm.getUserData()

        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.w = Workspace(self.user_data, self.user, self.csm)

    def getModule(self):

        return 'PerceptualAssociativeMemory (PAM)'

    def userData(self):
        return self.user_data
