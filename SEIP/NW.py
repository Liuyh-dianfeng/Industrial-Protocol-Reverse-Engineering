import numpy as np
import pandas as pd
from utils import *
########## NW_alignment
## If flag == 0, just return the final matrix, else, return the aligned sequences.

class NW(object):
    '''
    from NW import NW
    nw = NW(formula = '-2*abs(i-j)/255 + 1',punish = -0.1)
    str1 = ['02','02','00','c2','02','02','02','c0','01','0a']
    str2 = ['c0','01','09','c1','02','01','00','c2','02','01','02']

    score_matrix = nw.execute(str1,str2,0)
    score_matrix,s1,s2 = nw.execute(str1,str2,1)
    
    '''
    
    def __init__(self, formula = '1-2*(tanh(abs(i-j)/10))**2', punish = -0.7):
        A = np.zeros([257,257]) + np.eye(257)*1
        A[0,0] = punish
        for i in range(1,257):
            for j in range(1,257):
                if i != j :
                    A[i,j] = eval(formula)
                        #1-(tanh(x))^2,(0,1],[-1,1]，*2-1，1-2(tanh(x))^2
        for i in range(1,257):
            A[0,i] = punish
            A[i,0] = punish


        name_list=['_'] + ['{:02x}'.format(i) for i in range(256)]
        self.punish_matrix=pd.DataFrame(A,columns=name_list,index=name_list)
        self.punish = punish
    
    
    def execute(self,onestr, twostr,flag):
        str_one = strpreprocess(onestr,'bytelist')
        str_two = strpreprocess(twostr,'bytelist')
        s1 = []
        s2 = []
#         print('nw1: ',str_one)
#         print('nw2: ',str_two)
        index=["_"]+[i for i in str_one]
        columns=["_"]+[i for i in str_two]
        score_matrix=pd.DataFrame(np.zeros([len(str_one)+1,len(str_two)+1]),index=index,columns=columns)

        for i in range(len(str_one)+1):
            for j in range(len(str_two)+1):
                if i==0 or j ==0:
                    score_matrix.iloc[i,j]=0+self.punish*i+self.punish*j
                else:
                    insert=score_matrix.iloc[i,j-1]+self.punish
                    delect=score_matrix.iloc[i-1,j]+self.punish
                    match=score_matrix.iloc[i-1,j-1]+self.punish_matrix.loc[str_one[i-1],str_two[j-1]]
                    score_matrix.iloc[i, j]=max(insert,delect,match)

        i=len(str_one) 
        j=len(str_two)

        if flag==0:
            return score_matrix
        else:
            while (i > 0 or j > 0) :
                if i>0 and j>0:
                    insert=score_matrix.iloc[i,j-1]+self.punish
                    delect=score_matrix.iloc[i-1,j]+self.punish
                    match=score_matrix.iloc[i-1,j-1]+self.punish_matrix.loc[str_one[i-1],str_two[j-1]]

                    direction = np.argmax([match,insert,delect])
                    if direction == 1 and j>0:
                        s1.append('_')
                        s2.append(str_two[j - 1])
                        j -= 1
                    elif direction == 2 and i>0:
                        s1.append(str_one[i - 1])
                        s2.append('_')
                        i -= 1
                    elif direction == 0 and i>0 and j>0:
                        s1.append(str_one[i - 1])
                        s2.append(str_two[j - 1])
                        i -= 1
                        j -= 1
                    else:
                        print("error")
                        break
                elif j>0 and i == 0:
                    s1.append('_')
                    s2.append(str_two[j - 1])
                    j -= 1
                elif i>0 and j == 0:
                    s1.append(str_one[i - 1])
                    s2.append('_')
                    i -= 1
                else:
                    print("error2")

        #     print(score_matrix)
        #     print(s1[::-1],'\n',s2[::-1])
            return score_matrix,s1[::-1],s2[::-1]
