import pandas as pd
import numpy as np
from utils import *
######DTW
## If flag == 0, just return the final matrix, else, return the aligned sequences.

class DTW(object):
    
    def __init__(self,formula='abs(i-j)/255'):
        A = np.zeros([256,256])
        for i in range(256):
            for j in range(256):
                if i != j :
                    A[i,j] = eval(formula)
        name_list=['{:02x}'.format(i) for i in range(256)]
        self.distance_matrix = pd.DataFrame(A,columns=name_list,index=name_list)
    
    
    def execute(self, str_one, str_two, flag):
        s1 = []
        s2 = []

        index=[i for i in str_one]
        columns=[i for i in str_two]
        score_matrix=pd.DataFrame(np.zeros([len(str_one),len(str_two)]),index=index,columns=columns)

        for i in range(len(str_one)):
            for j in range(len(str_two)):
                if i==0 and j==0:
                    score_matrix.iloc[i,j]=self.distance_matrix.loc[str_one[i],str_two[j]]
                elif i==0 and j>0:
                    score_matrix.iloc[i,j]=self.distance_matrix.loc[str_one[i],str_two[j]] + score_matrix.iloc[i,j-1]
                elif j==0 and i>0:
                    score_matrix.iloc[i,j]=self.distance_matrix.loc[str_one[i],str_two[j]] + score_matrix.iloc[i-1,j]
                else:
                    insert=score_matrix.iloc[i,j-1]
                    delect=score_matrix.iloc[i-1,j]
                    match=score_matrix.iloc[i-1,j-1]
                    score_matrix.iloc[i, j]=min(insert,delect,match) + self.distance_matrix.loc[str_one[i],str_two[j]]

        i=len(str_one) -1
        j=len(str_two) -1
        s1.append(str_one[i])
        s2.append(str_two[j])
        if flag==0:
            return score_matrix
        else:
            while (i > 0 or j > 0) :
                if i>0 and j>0:
                    insert=score_matrix.iloc[i,j-1]
                    delect=score_matrix.iloc[i-1,j]
                    match=score_matrix.iloc[i-1,j-1]

                    direction = np.argmin([match,insert,delect])
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

    #         print(score_matrix)
    #         print(s1[::-1],'\n',s2[::-1])
            return score_matrix,s1[::-1],s2[::-1]
