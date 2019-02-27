from ProceduralMemory import ProceduralMemory
import pandas as pd
import numpy as np
#from pubsub import pub

class GlobalWorkspace:

    def __init__(self, df_from_attention_codelets, df_database, csm):

        self.df_database = df_database
        self.df_from_attention_codelets = df_from_attention_codelets
        self.df_to_procedural_memory = pd.DataFrame()

        self.csm = csm

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        #pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        #pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.pm= ProceduralMemory(self.winners(), self.df_database, self.csm)
        

    def competition(self):
        #Agrupar tabela ordenando por filmes
        self.df_from_attention_codelets = self.df_from_attention_codelets.sort_values(by=['movieId','rating'])

        #Avaliação média de cada filme
        avg_rating = self.df_from_attention_codelets.groupby(['movieId'])['rating'].mean()
        self.df_from_attention_codelets = self.df_from_attention_codelets.set_index(['movieId'])
        self.df_from_attention_codelets['avg_rating'] = avg_rating
        self.df_from_attention_codelets['avg_rating'] = self.df_from_attention_codelets.avg_rating.astype('float64')
        self.df_from_attention_codelets['avg_rating'] = self.df_from_attention_codelets.avg_rating.round(2)
        self.df_from_attention_codelets = self.df_from_attention_codelets.sort_values(by=['avg_rating'], ascending=False)

        #Limpando colunas
        self.df_from_attention_codelets = self.df_from_attention_codelets.drop(columns=['userId','rating'])

        self.df_from_attention_codelets = self.df_from_attention_codelets.drop_duplicates()
        self.df_from_attention_codelets = self.df_from_attention_codelets.reset_index(level=['movieId'])

        #Reagrupar tabela ordenando por filmes e avaliações
        self.df_from_attention_codelets = self.df_from_attention_codelets.sort_values(by=['avg_rating'], ascending=False)

    def winners(self):
        #Inicia competição
        self.competition()

        self.df_to_procedural_memory = self.df_from_attention_codelets
        
        print(self.df_to_procedural_memory)

        return self.df_to_procedural_memory

    def getModule(self):
        return 'Global Workspace'
