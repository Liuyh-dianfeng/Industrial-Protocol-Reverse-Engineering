import math
from utils import *
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt
        
class MsgEntropy:
    def __init__(self):
        self.dataset = []
        self.tplist = []
        self.hxlist = []
        self.dislist = []
        self.entro = []
        
    def init_para(self, messages):
        dataset = [strpreprocess(messages[i],'bytelist') for i in range(len(messages))]
        maxlen = len(max(dataset, key=len, default = ''))
        ### tplist = Msgs with position x / total Msgs
        ### hxlist = Entropy( position x )
        ### distlist = the sub-Entropy of each value in position x 
        tplist = []
        hxlist = []
        distlist = []
        for t in range(maxlen):
            column = []
            tsum = 0
            for i in range(len(dataset)):
                if t< len(dataset[i]):
                    column.append(dataset[i][t])
                else:
                    tsum +=1
            tplist.append(1- tsum/len(dataset))
            dist,hx = Entropy(column)
            distlist.append(dist)
            hxlist.append(hx)
        
        entro = np.array(hxlist)/np.array(tplist)
        
        self.dataset = dataset
        self.tplist = tplist
        self.hxlist = hxlist
        self.distlist = distlist
        self.entro = entro
    
    def plot_entro(self,messages):
        if len(self.tplist) < 2:
            self.init_para(messages)
        
        x = range(len(self.hxlist))
        plt.plot(x, np.array(self.hxlist)/np.array(self.tplist),marker='o',color = 'b')
        plt.show()
        return
    
    def single_entro(self,messages,mi):
        if len(self.tplist) < 2:
            self.init_para(messages)
        
        mentro = []
        for i in range(len(self.dataset[mi])):
            if self.entro[i] == 0:
                mentro.append(0)
            else:
                mentro.append(self.distlist[i][self.dataset[mi][i]]/(self.hxlist[i]*self.tplist[i]))
                
        return mentro
    
    def plot_single(self,messages,mi):
        mentro = self.single_entro(messages,mi)
        
        mx = range(len(self.dataset[mi]))
        plt.plot(mx,mentro,marker='x')
        plt.show()
        return
    
    def find_payloadpos(self,messages,start=5, end=2/5, gap=2):
        if len(self.tplist) < 2:
            self.init_para(messages)
            
        
        y = savgol_filter(self.entro, 11, 3)
        x = range(len(self.entro))
        
#         plt.plot(x, y,marker='o',color = 'b')
#         plt.show()
        
        v,y_v = val_eb(x[start:int(len(y)*end)],y[start:int(len(y)*end)],gap)
        i = y_v[v.index(max(v))]
        finalpos = i+start
        
        return finalpos
    
    def find_singlepos(self,messages,mi,start=5, end=2/5, gap=2):
        mentro = self.single_entro(messages, mi)
        
        y = savgol_filter(mentro, 11, 3)
        x = range(len(mentro))
#         plt.plot(x, y,marker='o',color = 'b')
#         plt.show()
        
        v,y_v = val_eb(x[start:int(len(y)*end)],y[start:int(len(y)*end)],gap)
        i = y_v[v.index(max(v))]
        finalpos = i+start
        
        return finalpos
    
    
def val_eb(x,y,gap):
    col=[]
    y_col = []
    for i in range(len(y) - gap):
        col.append((y[i + gap] - y[i]) / gap)
        y_col.append(i)
    return col,y_col
    pass    
    
def Entropy(x):
    dist = {}
    for i in range(len(x)):
        if x[i] not in dist:
            dist.update({x[i]:x.count(x[i])})
    hx = 0
    for key in dist:
        p = dist[key]/len(x)
        hxt = -p*math.log(p,2)
        dist[key] = hxt
        hx += hxt
    return dist, hx