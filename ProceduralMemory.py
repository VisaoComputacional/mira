from ActionSelection import ActionSelection
import pandas as pd
import numpy as np
from pubsub import pub

class ProceduralMemory:

    def __init__(self, df_procedural_memory, df_database, csm):

        self.df_procedural_memory = df_procedural_memory
        self.df_database = df_database
        self.csm = csm

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.df_database = self.df_database.loc[:,['movieId', 'title', 'genres','avg_rating']]
        
        self.list_category= ['Comedy Movies', 'Romantic Comedy Movies', 'Action/Adventure Movies', 'Crime/Drama Movies', 'Documentary', 'Drama Movies', 'Movies Late At Night', 'Musical/Thriller Movies']
        
        
        
        self.selected_movies = self.df_procedural_memory.head(40)
        index= int(self.df_procedural_memory.loc[0, 'cluster'])
        self.selected_movies = self.selected_movies['movieId'].tolist()
        self.action_selection = self.df_database[self.df_database.movieId.isin(self.selected_movies)]
        self.action_selection = self.action_selection.drop_duplicates(subset=['title'])
        aux= self.action_selection['title'].tolist()
        self.action_selection = pd.DataFrame(data=aux,columns= [self.list_category[index]])

        ActionSelection(self.action_selection, self.csm)

    def getModule(self):
        return 'Procedural Memory'
