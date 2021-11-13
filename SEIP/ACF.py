from statsmodels.tsa.stattools import acf
import numpy as np
import pandas as pd
from utils import *
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
### threshold is the min len of sub-message, which is 3

class ACF(object):
    def __init__(self, threshold = 3, alpha = .05):
        self.threshold = threshold
        self.alpha = alpha
    #### choose the first one which is larger than the confidence interval
    def execute_confi(self,str_one):
        str_one_t = strpreprocess(str_one, 'intlist')
        temp_flag = 0
        temp_alpha = self.alpha
        while(temp_flag == 0):
            temp_two = acf(np.array(str_one_t),nlags=int((len(str_one_t))/2),fft=False,alpha=temp_alpha)
            for j in range(self.threshold,len(temp_two[0])):
                if temp_two[0][j] > (temp_two[1][j][1] - temp_two[0][j]):
                    temp_index = j
                    temp_flag = 1
                    break
            temp_alpha += .05
        str_two = str_one[:temp_index]
        return temp_index
    #### choose the max one 
    def execute(self,onestr):
        str_one = strpreprocess(onestr,'intlist')
        temp_two,_ = acf(np.array(str_one),nlags=int((len(str_one))/2),fft=False,alpha=self.alpha)#<class 'numpy.ndarray'>
        temp_two[:self.threshold] = 0
        temp_two = list(temp_two)
        index = temp_two.index(max(temp_two))
        return index
    
    
    def plotACF(self,onestr):
        str_one = np.array(strpreprocess(onestr,'intlist'))
        fig = plt.figure()
        plot_acf(str_one,lags = int(len(str_one)-1),zero=False)
        plt.show()
        