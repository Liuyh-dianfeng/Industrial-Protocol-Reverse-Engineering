from utils import *
from netzob.all import *
import numpy as np
from TrueCommand import *
#!pip install lda
import lda
from collections import Counter

class LDA:
    def __init__(self, n_topics=10,n_iter=15000,random_state = 1):
        self.n_topics = n_topics
        self.n_iter = n_iter
        self.random_state = random_state
        
    def execute(self, file, best_flag = 0):
        if type(file) == str:
            datalist = filepreprocess(file)
        elif type(file) == list or type(file) == np.ndarray:
            datalist = file
        else:
            return  'error'
        
        
        data = [strpreprocess(datalist[i],'bytelist') for i in range(len(datalist))]

        label = [s7type(data[i]) for i in range(len(data))]
        
        labelcoding = Coding(label)
        
        vocdic= tuple(['{:02x}'.format(i) for i in range(256)])
        
        Xlist = []
        for i in range(len(data)):
            temp = np.zeros(256).astype(int)
            for j in range(len(data[i])):
                temp[int(data[i][j],16)] += 1
            Xlist.append(temp)
        
        if best_flag == 0:
            model = lda.LDA(n_topics=self.n_topics,n_iter=self.n_iter,random_state = self.random_state)
        else:
            best_n_topic = len(Counter(label))
            model = lda.LDA(n_topics=best_n_topics,n_iter=self.n_iter,random_state = self.random_state)
            
        model.fit(np.array(Xlist))
        
        
        doc_topic = model.doc_topic_
        inferlabel = [doc_topic[i].argmax() for i in range(len(doc_topic))]
        
        score = ClusterScore(labelcoding,inferlabel)
        
        return score, inferlabel