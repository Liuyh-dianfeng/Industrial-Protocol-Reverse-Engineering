import numpy as np
import pandas as pd
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count
from NW import NW
from DTW import DTW
from utils import *

class Segmentation(object):
    
    def __init__(self, executor, cpu = 0):
        self.mode = type(executor).__name__
        self.executor = executor
        self.cpu = cpu
        
    def execute(self, onestr, twostr):
#         print('twostrseg:',twostr)
#         print('twostrtype:',type(twostr[0]))
        str_one = strpreprocess(onestr,'bytelist')
        str_two = strpreprocess(twostr,'bytelist')
#         print('seg: ',str_two)
        f_index = [i for i in range(len(str_one))]
        f_columns = [i for i in range(len(str_one))]
        final_matrix=pd.DataFrame(np.zeros([len(str_one),len(str_one)]),index=f_index,columns=f_columns)
        
        ##################
        if self.cpu == 0:
            if self.mode == 'NW':
                for i in range(len(str_one)):
                    score_matrix = self.executor.execute(str_one[i:], str_two, 0)

                    scores_temp = list(score_matrix.iloc[1:,len(str_two)].values[:])

                    final_matrix.iloc[i,:] = [np.nan for k in range(i)] + scores_temp
            else:
                for i in range(len(str_one)):
                    score_matrix = self.executor.execute(str_one[i:], str_two, 0)

                    scores_temp = list(score_matrix.iloc[:,len(str_two)-1].values[:])
                    #每一个值都做个长度补偿
                    for j in range(len(scores_temp)):

                        scores_temp[j] = scores_temp[j]**2

                    final_matrix.iloc[i,:] = [np.nan for k in range(i)] + scores_temp
        ##################
        else:    
            PROCESSES = cpu_count()
            if PROCESSES > 20:
                PROCESSES = 20

            #NW for every line
            TASKS1 = [(self.executor.execute, (str_one[i:], str_two, 0), i) for i in range(len(str_one))]


            task_queue = Queue()
            done_queue = Queue()

            # Submit tasks
            for task in TASKS1:
                task_queue.put(task)

            # Start worker processes
            for i in range(PROCESSES):
                Process(target=worker, args=(task_queue, done_queue)).start()

            # Get and print results
    #         print('Unordered results:')
            for i in range(len(TASKS1)):
                temp = done_queue.get()
    #             print('temp: ', temp)
                if self.mode == 'NW':
                    scores_temp = list(temp[0].iloc[1:,len(str_two)].values[:])
                elif self.mode == 'DTW':
                    scores_temp = list(temp[0].iloc[:,len(str_two)-1].values[:])
                    for j in range(len(scores_temp)):
                        scores_temp[j] = scores_temp[j]**2
                else:
                    print('mode error!')
                final_matrix.iloc[temp[1],:] = [np.nan for k in range(temp[1])] + scores_temp


            for i in range(PROCESSES):
                task_queue.put('STOP')
        ###################
#         print('final_matrix:',final_matrix)
        ################ update
#         for i in range(1,len(str_one)):
#             for j in range(i,len(str_one)):
#                 if i == j:
#                     temp = final_matrix.iloc[i,j] + final_matrix.iloc[i-1,j-1]
#                     temp_list = list(final_matrix.iloc[:i-1,j].values) + [temp]
#                     if self.mode == 'NW':
#                         final_matrix.iloc[i,j] = max(temp_list)
#                     elif self.mode == 'DTW':
#                         final_matrix.iloc[i,j] = min(temp_list)
#                     else:
#                         print('mode error!')
#                 else:
#                     final_matrix.iloc[i,j] += final_matrix.iloc[i-1,i-1]
        ###add the max last column            
        for i in range(1,len(str_one)):
            for j in range(i,len(str_one)):
                final_matrix.iloc[i,j] += max(list(final_matrix.iloc[:i,i-1]))
#         print("final_matrix_update:",final_matrix)
        #####################
        final_score = final_matrix.iloc[len(str_one)-1,len(str_one)-1]
#         print("final_score:",final_score)

        i = len(str_one)-1
        final_pos = []
        final_pos.append(i+1)
        #########
#         while(i>0):
#             temp = list(final_matrix.iloc[:,i].values)[:i]
#         #         temp_index = temp.index(max(temp))
#             if self.mode == 'NW':
#                 temp_index = temp.index(max(temp))
#             elif self.mode == 'DTW':
#                 temp_index = temp.index(min(temp))
#             else:
#                 print('mode error!')
#         #         print("temp:",temp)
#         #         print("temp_index:",temp_index)
#             final_pos.append(temp_index)
#             if temp_index == 0:
#                 break
#             i = temp_index - 1
        ###
        while(i>0):
            temp = list(final_matrix.iloc[:,i].values)[:i+1]
        #         temp_index = temp.index(max(temp))
            if self.mode == 'NW':
                temp_index = temp.index(max(temp))
            elif self.mode == 'DTW':
                temp_index = temp.index(min(temp))
            else:
                print('mode error!')
        #         print("temp:",temp)
        #         print("temp_index:",temp_index)
            final_pos.append(temp_index)
            if temp_index == 0:
                break
            i = temp_index - 1
            
        #######    
        final_pos = final_pos[::-1]
#         print("final_pos_t:",final_pos) 

        onepos = final_pos


        if len(str_one) > onepos[-1]:
            onepos[-1] = len(str_one)
    #         print('xiuzheng')

        one_seqs = []
        #     one_seqs.append(str_one_ogl[:onepos[0]])
        for i in range(len(onepos)-1):
            one_seqs.append(str_one[onepos[i]:onepos[i+1]])
    #     print('one_seqs:', one_seqs)
    
        return one_seqs,onepos,final_score
