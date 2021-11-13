from scipy.spatial import distance
import numpy as np
import pandas as pd
import scipy.stats
from utils import *

def alignstrategy(str1,str2,flag):
    str1t = strpreprocess(str1,'intlist')
    str2t = strpreprocess(str2,'intlist')
    str1b = strpreprocess(str1,'bytelist')
    str2b = strpreprocess(str2,'bytelist')
    if flag == 'backzero':
        while(len(str1t)>len(str2t)):
            str2t.append(0)
        while(len(str2t)>len(str1t)):
            str1t.append(0)
    if flag == 'NWpure':
        from NW import NW
        nw = NW(formula = 'int(i==j)', punish = 0)
        _,str1b,str2b = nw.execute(str1b,str2b,1)
        str1t = [int(str1b[i],16) if str1b[i] != '_' else 0 for i in range(len(str1b))]
        str2t = [int(str2b[i],16) if str2b[i] != '_' else 0 for i in range(len(str2b))]
    if flag == 'NWamend':
        from NW import NW
        nw = NW()
        _,str1b,str2b = nw.execute(str1b,str2b,1)
        str1t = [int(str1b[i],16) if str1b[i] != '_' else 0 for i in range(len(str1b))]
        str2t = [int(str2b[i],16) if str2b[i] != '_' else 0 for i in range(len(str2b))]
    return str1t,str2t
        
def DisBraycurtis(str1, str2, flag='backzero'):
    ##small is best
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.braycurtis(str1t,str2t)
    return dis

def DisCanberra(str1,str2, flag='backzero'):
    ##small is best
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.canberra(str1t,str2t)
    return dis

def DisMinkowski(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.wminkowski(str1t,str2t,2,np.ones(len(str1t)))
    return dis

def DisChebyshev(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.chebyshev(str1t,str2t)
    return dis

def DisCityblock(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.cityblock(str1t,str2t)
    return dis

def DisSqeuclidean(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.sqeuclidean(str1t,str2t)
    return dis

def DisCosine(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.cosine(str1t,str2t)
    return dis

def DisCorrelation(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.correlation(str1t,str2t)
    return dis

def DisDice(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.dice(str1t,str2t)
    return dis

def DisJaccard(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.jaccard(str1t,str2t)
    return dis

def DisKulsinski(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.kulsinski(str1t,str2t)
    return dis

def DisSokalmichener(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.sokalmichener(str1t,str2t)
    return dis

def DisSokalsneath(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.sokalsneath(str1t,str2t)
    return dis

def DisYule(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.yule(str1t,str2t)
    return dis

def DisRussellrao(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.russellrao(str1t,str2t)
    return dis

def DisHamming(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    dis = distance.hamming(str1t,str2t)
    return dis

def DisLevenshtein(str1,str2, flag='backzero'):
    str1t = strpreprocess(str1,'str')
    str2t = strpreprocess(str2,'str')
    import Levenshtein
    dis = Levenshtein.distance(str1t,str2t)
    return dis

def DisKendall(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    str1t = pd.Series(str1t)
    str2t = pd.Series(str2t)
    dis = str1t.corr(str2t, method = 'kendall')
    return dis

def DisKL(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    str1t = np.asarray(str1t)
    str2t = np.asarray(str2t)
    dis = scipy.stats.entropy(str1t,str2t)
    return dis

def DisJS(str1,str2, flag='backzero'):
    str1t,str2t = alignstrategy(str1,str2,flag)
    str1t = np.asarray(str1t)
    str2t = np.asarray(str2t)
    M = (str1t + str2t) / 2
    dis = 0.5*scipy.stats.entropy(str1t,M) + 0.5*scipy.stats.entropy(str2t,M)
    return dis