from PerceptualAssociativeMemory import PerceptualAssociativeMemory
from pubsub import pub

class SensoryMemory:

    def __init__(self, user, csm):

        self.user = user

        self.csm = csm

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.pam = PerceptualAssociativeMemory(self.user, self.csm)

    def getUser(self):
        return self.user

    def setUser(self, user):
        self.user = user

    def getModule(self):
        return 'Sensory Memory'
