import pandas as pd
import numpy as np
from pubsub import pub

class ActionSelection:

    def __init__(self, action_selection, csm):

        self.action_selection = action_selection
        self.csm = csm

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        print(self.action_selection.to_string(index=False))

    def getModule(self):
        return 'Action Selection'
