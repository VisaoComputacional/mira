from Workspace import CurrentSituationalModel
from SensoryMemory import SensoryMemory
from pubsub import pub
import pandas as pd

class Environment:

    def __init__(self):

        self.csm = CurrentSituationalModel()

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)
        
        self.user = int(input('Insira o userID: '))
        self.sm = SensoryMemory(self.user, self.csm)

    def getModule(self):

        return 'Environment'
