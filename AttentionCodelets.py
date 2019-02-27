from GlobalWorkspace import GlobalWorkspace
import pandas as pd
import numpy as np
import pickle
from pubsub import pub
from sklearn.cluster import KMeans
import imp
import re

class AttentionCodelets:

    '''
    df_main_user: dataframe do usuário principal do sistema. Colunas: movieId|cluster
    df_from_workspace: dataframe recebido do workspace com cluster dos usuários semelhantes
    ao usuário principal. Colunas: userId|movieId|cluster
    '''

    def __init__(self, df_from_workspace, df_main_user, database, csm):
        self.df_main_user = df_main_user
        self.df_from_workspace = df_from_workspace
        self.df_to_global_workspace = pd.DataFrame()
        self.database = database
        self.csm = csm
        self.df_original = database

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        self.gwt = GlobalWorkspace(self.relevant_contents(), self.database, self.csm)

    def get_df_main_user(self):
        return self.df_main_user

    def get_df_from_workspace(self):
        return self.df_from_workspace

    def get_df_to_global_workspace(self):
        return self.df_to_global_workspace

    def clustering_main_user(self):
        '''
        Função que clusteriza os filmes do usuário principal do sistema
        '''

        #Copia primeira linha do dataframe do usuário principal e insere na última posição do dataframe
        self.df_main_user = self.df_main_user.append(self.df_main_user.iloc[0],ignore_index=True)

        #Adiciona na coluna 'genres' da primeira linha do dataframe o padrão de gêneros a ser clusterizado
        self.df_main_user.loc[0,'genres'] = 'Action|Adventure|Animation|Children|Comedy|Crime|Documentary|Drama|Fantasy|Film-Noir|Horror|Musical|Mystery|Romance|Sci-Fi|Thriller|War|Western'

        #Separa as duas colunas de interesse 'movieId' e 'genres' do dataframe do usuário principal
        self.df_main_user = self.df_main_user.loc[:,['movieId','genres']]

        #Classifica os dados em dummies de 'movieId' X 'genres'
        self.df_main_user = self.df_main_user.set_index('movieId').genres.str.get_dummies(sep='|').reset_index()

        #Exclui colunas que não estão inclusas no modelo
        try:
            self.df_main_user.drop(['(no genres listed)'], axis=1, inplace=True)

        except ValueError:
            pass

        except KeyError:
            pass

        try:
            self.df_main_user.drop(['IMAX'], axis=1, inplace=True)

        except ValueError:
            pass

        except KeyError:
            pass

        #Exclui primeira linha inserida para padronizar gêneros
        self.df_main_user = self.df_main_user.drop([0])

        #Transforma os dados do dummies em array de valores
        X = self.df_main_user.iloc[:,1:19].values

        #Carrega modelo pré classificado K-Means de clusters de gênero
        modelo = pickle.load(open('data/modelo_cluster_8.sav','rb'))

        #Adiciona coluna cluster já definida pelo modelo
        self.df_main_user['cluster'] = modelo.predict(X)

        #Seleciona as colunas principais do usuário: 'movieId' e 'cluster'
        self.df_main_user = self.df_main_user.loc[:,['movieId','cluster']]

        return self.df_main_user

    def relevant_contents(self):

        '''
        Função que identifica a qual cluster pertence o usuário principal e seleciona todos os filmes desse cluster.
        No final ainda são atribuídas as avaliações de cada filme
        '''

        #Recebe os dados do usuário principal clusterizado
        df_main_user_clustered = self.clustering_main_user()

        #Calcula frequencias dos clusters do usuário principal
        df_frequencies= df_main_user_clustered['cluster'].value_counts()

        #Seleciona o cluster de maior valor
        aux = df_frequencies.max()

        #Identifica qual o cluster de maior frequencia
        main_user_cluster = df_frequencies[df_frequencies == aux].index[0]

        #Seleciona todos os filmes que pertencem apenas ao cluster definido do usuário principal
        self.df_from_workspace = self.df_from_workspace[self.df_from_workspace['cluster'].isin([main_user_cluster])]

        #Reseta o index do dataframe de filmes vindo do workspace
        self.df_from_workspace = self.df_from_workspace.reset_index(drop=True)

        #Atribui a lista filmes já assistidos pelo usuário
        lista_movieId = self.df_main_user['movieId'].tolist()

        #Seleciona apenas os filmes que o usuário ainda não assistiu
        self.df_from_workspace = self.df_from_workspace[(self.df_from_workspace['movieId'].isin(lista_movieId)) == False]

        #Seleciona colunas de interesse
        df_aux = self.df_original.loc[:,['userId','movieId','rating']]

        #Cruza base original com a base vinda do workspace para obter as avaliações
        self.df_to_global_workspace = self.df_from_workspace.merge(df_aux, how='inner', on=['userId','movieId'])
        
        return self.df_to_global_workspace


    def getModule(self):
        return 'Attention Codelets'
