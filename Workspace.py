from DeclarativeMemory import DeclarativeMemory
from AttentionCodelets import AttentionCodelets
#from pubsub import pub
import pandas as pd
import numpy as np
import pickle
import re
import imp
from sklearn.cluster import KMeans

class CurrentSituationalModel:

    def __init__(self):
        pass

    def listener(self, arg1, arg2=None):
        print('Agent is in', arg1 , 'module.')

class Workspace:

    def __init__(self, user_data, user_id, csm):

        self.csm = csm
        self.user_id = user_id

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        #pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        #pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.user_data = user_data

        # recebe dados do usuario da pam para enviar a memoria declarativa
        self.dm = DeclarativeMemory(self.user_id, self.csm)

        # procura na DeclarativeMemory os usuarios similares ao agente
        self.similar_users = self.dm.similar_users()

        # DeclarativeMemory retorna a base de dados
        self.database = self.dm.getDatabase()

        # envia dados da memoria declarativa para construir estruturas
        self.sbc = StructureBuildingCodelets(self.similar_users, self.csm)

        # prepara dataframe para enviar ao AttentionCodelets
        self.df_workspace = self.sbc.histogramBuilder()

        # segue para o modulo de AttentionCodelets
        self.ac = AttentionCodelets(self.df_workspace, self.user_data, self.database, self.csm)

    def getModule(self):
        return 'Workspace'


class StructureBuildingCodelets:

    def __init__(self, users_data, csm):

        self.users_data = users_data

        self.csm = csm

        #pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        #pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

    def histogramBuilder(self):

        # insere a primeira linha da base para a ultima
        self.users_data = self.users_data.append(self.users_data.iloc[0], ignore_index=True)

        # insere na primeira linha todos os generos para o histograma para classificar todos os generos
        self.users_data.loc[0,'genres'] = 'Action|Adventure|Animation|Children|Comedy|Crime|Documentary|Drama|Fantasy|Film-Noir|Horror|Musical|Mystery|Romance|Sci-Fi|Thriller|War|Western'

        # separa a coluna de generos
        self.users_data = self.users_data.set_index(['userId', 'movieId']).genres.str.get_dummies(sep='|').reset_index()

        try:
            self.users_data.drop(['(no genres listed)'], axis=1, inplace=True)

        except ValueError:
            pass

        except KeyError:
            pass

        try:
            self.users_data.drop(['IMAX'], axis=1, inplace=True)

        except ValueError:
            pass

        except KeyError:
            pass

        # insere os dados binarios das colunas de genero em uma matriz de arrays
        X = self.users_data.iloc[:,2:20].values

        # carrega modelo para gerar os clusters
        self.model = pickle.load(open('data/modelo_cluster_8.sav','rb'))

        # cria coluna de cluster e insere os valores do cluster do movieId
        self.users_data['cluster'] = self.model.predict(X)

        self.users_data = self.users_data.loc[:,['userId','movieId','cluster']]

        return self.users_data

    def getModule(self):
        return 'Workspace - Structure Building Codelets'
