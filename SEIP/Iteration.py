import numpy as np
import pandas as pd
from NW import NW
from DTW import DTW
from Segmentation import Segmentation
from TemplateUpdate import TemplateUpdate
from utils import *
import copy

class Iteration(object):
    
    def __init__(self,executor,iterations = 10,thetat = .9,cpu=0):
        self.executor = executor
        self.mode = type(executor).__name__
        self.iterations = iterations
        self.thetat = thetat
        self.cpu = cpu
        
        
    def execute(self,onestr,twostr):
        str_one = strpreprocess(onestr,'bytelist')
#         print('iter1:',str_one)
        str_two = strpreprocess(twostr,'bytelist')
#         print('iter2:',str_two)
        str_two_t = copy.deepcopy(str_two)
        iterations_list = []
        iterations_list.append(str_two_t)
        seg = Segmentation(executor = self.executor,cpu=self.cpu)
        tmp = TemplateUpdate(executor = self.executor,cpu=self.cpu)
        
        for iterations in range(self.iterations):
#             print(str_one)
#             print(str_two_t)
            oneseqs, final_pos, final_score = seg.execute(str_one,str_two_t)
            
#             print('iterations_list: ',iterations_list)
            new_two_seq, one_seqs = tmp.execute(one_seqs = oneseqs)
#             print('new_two_seq: ',new_two_seq)
            if new_two_seq in iterations_list:
#                 print('iterations_inhistory:',iterations_list.index(new_two_seq))
                break
            else:
                iterations_list.append(new_two_seq)
            

            score_t= self.executor.execute(str_two_t,new_two_seq,0)
#             if iterations < 5:
#             	if new_two_seq == str_two:
#             	    print('iterations_same:',iterations)
#                     break
            if self.mode == 'NW':
                score = score_t.iloc[len(str_two_t),len(new_two_seq)]
                if score >= max(len(str_two_t),len(new_two_seq))*self.thetat:
#                     print('iterations_nw:',iterations)
                    break
                
            elif self.mode == 'DTW':
                score = score_t.iloc[len(str_two_t)-1,len(new_two_seq)-1]
                if score <= len(str_two_t)*(1-self.thetat)/10:
#                     print('iterations_dtw:',iterations)
                    break
            else:
                print("mode error!")
            
            str_two_t = copy.deepcopy(new_two_seq)
        
        return iterations, final_pos, one_seqs, new_two_seq, final_score
        
