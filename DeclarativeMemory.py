from pubsub import pub
import pandas as pd
import numpy as np
from scipy.sparse.dok import dok_matrix

class DeclarativeMemory:

    def __init__(self, user_id, csm):

        self.user_id = user_id
        self.csm = csm
        self.users_list = []

        # se inscreve no topico CurrentSituationalModel e publica o status do ambiente
        pub.subscribe(self.csm.listener, 'CurrentSituationalModel')
        pub.sendMessage('CurrentSituationalModel', arg1=self.getModule(), arg2=None)

        # carrega arquivo com as colunas userId|movieId|genres
        self.database = pd.read_csv('data/movies_ratings.csv', encoding = 'utf-8', sep=';')

    def train_test_split(self, ratings):

        test = np.zeros(ratings.shape)
        train = ratings.copy()

        for user in range(ratings.shape[0]):
            test_ratings = np.random.choice(ratings[user, :].nonzero()[0], size=10, replace=False)
            train[user, test_ratings] = 0.
            test[user, test_ratings] = ratings[user, test_ratings]

        # Test and training are truly disjoint
        assert(np.all((train * test) == 0))
        return train, test;

    def fast_similarity(self, ratings, kind='user', epsilon=1e-9):

        # epsilon -> small number for handling dived-by-zero errors
        if kind == 'user':
            sim = ratings.dot(ratings.T) + epsilon
        elif kind == 'item':
            sim = ratings.T.dot(ratings) + epsilon

        norms = np.array([np.sqrt(np.diagonal(sim))])

        return (sim / norms / norms.T)

    def similar_users(self, qte_users = 50):

        names = ['user_id', 'item_id', 'rating', 'timestamp']
        df = pd.read_csv('data/u.data', sep='\t', names=names)      # leitura do arquivo de avaliações

        n_users = df.user_id.unique().shape[0]                 #quantidade de usuarios
        n_items = df.item_id.unique().shape[0]                 #quantidade de itens
        
        ratings = np.zeros((n_users, n_items*2))
        
        #Bigrams = dok_matrix(x, n)
        for row in df.itertuples():
            ratings[row[1]-1, row[2]-1] = row[3]

        train, test = self.train_test_split(ratings)

        self.user_similarity = self.fast_similarity(train, kind='user')
        self.user_similarity.resize(len(self.user_similarity)+1,len(self.user_similarity)+1)
        # item_similarity = fast_similarity(train, kind='item')

        lista = []
        self.similarity_list = self.user_similarity[self.user_id, :]

        for i in range(0, len(test)):
            lista.append((self.similarity_list[i], i))

        lista.sort(reverse=True)

        for i in range(0, qte_users):
            if lista[i][0] < 1.0: self.users_list.append(lista[i][1])

        # seleciona as linhas conforme a lista de usuarios
        self.database = self.database[self.database.userId.isin(self.users_list)]

        return self.database

    def getModule(self):
        return 'Declarative Memory'

    def getDatabase(self):
        return self.database

    def getUserData(self):
        user_data = self.database[self.database['userId']==self.user_id]
        return user_data
