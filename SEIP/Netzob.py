from netzob.all import *
from netzob.Inference.Vocabulary.FormatOperations.ClusterByAlignment import ClusterByAlignment
from utils import *
from TrueCommand import *

class Netzob:
    def __init__(self):
        self.method = None
        
    def cluster(self, file, minEq=55):
        if type(file) == str:
            datalist = filepreprocess(file)
        elif type(file) == list or type(file) == np.ndarray:
            datalist = file
        else:
            return  'error'
        
        data = [strpreprocess(datalist[i],'str').encode('utf-8') for i in range(len(datalist))]
        
        data = [RawMessage(data[i]) for i in range(len(data))]
        
        clustering = ClusterByAlignment(minEquivalence = minEq)
        
        symbols = clustering.cluster(data)
        
        cluster  = [[] for i in range(len(symbols))]
        true = [[] for i in range(len(symbols))]

        for i in range(len(symbols)):
#             print('i: ',i)
            kk = 0
            for message in symbols[i].messages:
        #         print(message)
                temp = str(message.data, encoding = 'utf-8')
#                 print(temp)
#                 print(s7type(temp))
                cluster[i].append(temp)
                true[i].append(s7type(temp))
                kk+=1
        
        labels = {}
        clustersfinal = []
        clusterstrue = []
        t = 0
        for i in range(len(true)):
            for j in range(len(true[i])):
                if true[i][j] not in labels:
                    labels.update({true[i][j]:t})
                    t+=1
                clustersfinal.append(i)
                clusterstrue.append(labels[true[i][j]])
                
        score = ClusterScore(clusterstrue,clustersfinal)
        
        return score,clustersfinal