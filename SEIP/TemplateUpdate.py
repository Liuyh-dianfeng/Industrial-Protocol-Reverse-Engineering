import numpy as np
import pandas as pd
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count
from NW import NW
from DTW import DTW
from utils import *
import copy
import random

class TemplateUpdate(object):
    
    def __init__(self,executor,thetag = 0.4,cpu=0):
        self.executor = executor
        self.mode = type(executor).__name__
        self.thetag = thetag
        self.cpu= cpu
    
    def execute(self,one_seqs):
        one_seqs_t = copy.deepcopy(one_seqs)
        ### MSA_amended
        MSA_index = [i for i in range(len(one_seqs_t))]
        MSA_columns = [i for i in range(len(one_seqs_t))]
        MSA_scores = pd.DataFrame(np.zeros([len(one_seqs_t),len(one_seqs_t)]),index=MSA_index,columns=MSA_columns)
        
        
        ##################
        if self.cpu == 0:
            if self.mode == 'NW':
                for i in range(len(one_seqs_t)):
                    for j in range(i+1,len(one_seqs_t)):
                        score_t = self.executor.execute(one_seqs_t[i], one_seqs_t[j], 0)
                        MSA_scores.iloc[i,j] = score_t.iloc[len(one_seqs_t[i]),len(one_seqs_t[j])]
            else:
                for i in range(len(one_seqs_t)):
                    for j in range(i+1,len(one_seqs_t)):
                        score_t = self.executor.execute(one_seqs_t[i], one_seqs_t[j], 0)
                        MSA_scores.iloc[i,j] = score_t.iloc[len(one_seqs_t[i])-1,len(one_seqs_t[j])-1]
        ##################
        else:
            PROCESSES = cpu_count()
            if PROCESSES > 20:
                PROCESSES = 20
            #NW for every line
            TASKS1 = [(self.executor.execute, (one_seqs_t[i], one_seqs_t[j], 0), (i,j)) for i in range(len(one_seqs_t)) for j in range(i+1,len(one_seqs_t))]


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
                    MSA_scores.iloc[temp[1][0], temp[1][1]] = temp[0].iloc[len(one_seqs_t[temp[1][0]]),len(one_seqs_t[temp[1][1]])]
                elif self.mode == 'DTW':
                    MSA_scores.iloc[temp[1][0], temp[1][1]] = temp[0].iloc[len(one_seqs_t[temp[1][0]]) - 1,len(one_seqs_t[temp[1][1]]) - 1]
                else:
                    print('mode error!')

            for i in range(PROCESSES):
                task_queue.put('STOP')
        
        
        
        for i in range(len(one_seqs_t)):
            for j in range(0,i+1):
                MSA_scores.iloc[i,j] = np.nan
    #     print("MSA_scores:",MSA_scores)


        MSA_index = [[] for i in range(len(one_seqs_t))]
        for tt in range(len(one_seqs_t) - 1):
            ###merge
            if self.mode == 'NW':
                MSA_scores_min = MSA_scores[MSA_scores==MSA_scores.max().max()].dropna(axis=1, thresh=1).dropna(thresh=1)
            elif self.mode == 'DTW':
                MSA_scores_min = MSA_scores[MSA_scores==MSA_scores.min().min()].dropna(axis=1, thresh=1).dropna(thresh=1)
            else:
                print("mode error!")
            MSA_scores_min_index = MSA_scores_min.index[0]
            MSA_scores_min_columns = MSA_scores_min.columns[0]
    #         print("MSA_scores_min_index:",MSA_scores_min_index)
    #         print("MSA_scores_min_columns:",MSA_scores_min_columns)
            score_t, s1_t, s2_t = self.executor.execute(one_seqs_t[MSA_scores_min_index], one_seqs_t[MSA_scores_min_columns], 1)
    #         print('s1_t: ',s1_t)
    #         print('s2_t: ',s2_t)

            s1_list = []
            q1 = Queue()
            q1.put(MSA_scores_min_index)
            while(q1.qsize() > 0):
                temp_index = q1.get()
                s1_list.append(temp_index)
                for i in range(len(MSA_index[temp_index])):
                    q1.put(MSA_index[temp_index][i])
    #         print('s1_list: ',s1_list)

            s2_list = []
            q2 = Queue()
            q2.put(MSA_scores_min_columns)
            while(q2.qsize() > 0):
                temp_index = q2.get()
                s2_list.append(temp_index)
                for i in range(len(MSA_index[temp_index])):
                    q2.put(MSA_index[temp_index][i])
    #         print('s2_list: ',s2_list)

            for i in range(len(s1_t)):
                if s1_t[i] == '_':
                    for j in s1_list:
                        one_seqs[j].insert(i,'_')
                if s2_t[i] == '_':
                    for j in s2_list:
                        one_seqs[j].insert(i,'_')

    #         print('mended:')
    #         for i in (s1_list + s2_list):
    #             print(one_seqs[i])

            sMerge = []
            for i in range(len(s1_t)):
                temp_list = [one_seqs[j][i] for j in (s1_list + s2_list)]
                while('_' in temp_list):
                    temp_list.remove('_')
                if len(temp_list) > 0:
                    sMerge.append('{:02x}'.format(int(np.mean([int(temp_list[j],16) for j in range(len(temp_list))]))))
    #         print('sMerge: ',sMerge)

            MSA_index[MSA_scores_min_index].append(MSA_scores_min_columns)

            one_seqs_t[MSA_scores_min_index] = sMerge

            for i in range(MSA_scores_min_columns):
                MSA_scores.iloc[i,MSA_scores_min_columns] = np.nan

            for i in range(MSA_scores_min_columns+1,len(one_seqs_t)):
                MSA_scores.iloc[MSA_scores_min_columns,i] = np.nan

            for i in range(MSA_scores_min_index):
                if np.isnan(MSA_scores.iloc[i,MSA_scores_min_index]):
                    continue
                else:
                    score_t= self.executor.execute(one_seqs_t[i], one_seqs_t[MSA_scores_min_index], 0)
                    if self.mode == 'NW':
                        MSA_scores.iloc[i,MSA_scores_min_index] = score_t.iloc[len(one_seqs_t[i]),len(one_seqs_t[MSA_scores_min_index])]
                    elif self.mode == 'DTW':
                        MSA_scores.iloc[i,MSA_scores_min_index] = score_t.iloc[len(one_seqs_t[i])-1,len(one_seqs_t[MSA_scores_min_index])-1]
                    else:
                        print("mode error!")
            for i in range(MSA_scores_min_index+1,len(one_seqs_t)):
                if np.isnan(MSA_scores.iloc[MSA_scores_min_index,i]):
                    continue
                else:
                    score_t= self.executor.execute(one_seqs_t[i], one_seqs_t[MSA_scores_min_index], 0)
                    if self.mode == 'NW':
                        MSA_scores.iloc[MSA_scores_min_index,i] = score_t.iloc[len(one_seqs_t[i]),len(one_seqs_t[MSA_scores_min_index])]
                    elif self.mode == 'DTW':
                        MSA_scores.iloc[MSA_scores_min_index,i] = score_t.iloc[len(one_seqs_t[i])-1,len(one_seqs_t[MSA_scores_min_index])-1]
                    else:
                        print("mode error!")
    #         print("MSA_scores-mended:",MSA_scores)

        one_seqs = np.array(one_seqs)
        new_two_seq = []
        gap_num = 0
        for i in range(len(one_seqs[0])):
            temp_l = list(one_seqs[:,i])
            _num = temp_l.count('_')
            if _num > len(temp_l)*self.thetag:
                gap_num += 1
                continue
            else:
                while('_' in temp_l):
                    temp_l.remove('_')
                new_two_seq.append('{:02x}'.format(int(round(np.mean([int(temp_l[j],16) for j in range(len(temp_l))])))))
        
        if len(one_seqs)>=4:
            if (gap_num >= len(one_seqs[0])*0.4) or (list(one_seqs[0]).count('_') >= len(one_seqs[0])*0.4) or (list(one_seqs[1]).count('_') >= len(one_seqs[1])*0.4):
                new_two_seq_t = np.array(list(one_seqs[0]) + list(one_seqs[1]))
                gap_pos = np.where(new_two_seq_t != '_')
                new_two_seq = list(new_two_seq_t[gap_pos])

        
        tmpseqs_pos = np.where(one_seqs[0] != '_')
        tmpseqs = one_seqs[0][tmpseqs_pos]
        if len(one_seqs[0]) >= 30:
            new_two_seq = list(tmpseqs[:int(len(tmpseqs)/2 + random.choice([-1,0,1]))])
        elif len(tmpseqs) < 3:
            new_two_seq_t = np.array(list(one_seqs[0]) + list(one_seqs[1]))
            gap_pos = np.where(new_two_seq_t != '_')
            new_two_seq = list(new_two_seq_t[gap_pos])
        else:
            tmpseqs1 = tmpseqs[:int(len(tmpseqs)/2)]
            tmpseqs2 = tmpseqs[int(len(tmpseqs)/2):]
            tmpseqsscore = self.executor.execute(tmpseqs1, tmpseqs2, 0)
            if self.mode == 'NW':
                if tmpseqsscore.iloc[len(tmpseqs1),len(tmpseqs2)] >= len(tmpseqs)/2 * 0.6:
                    new_two_seq = list(tmpseqs1)
            elif self.mode == 'DTW':
                if tmpseqsscore.iloc[len(tmpseqs1)-1,len(tmpseqs2)-1] <= len(tmpseqs)/2 * 0.1:
                    new_two_seq = list(tmpseqs1)
            else:
                print('mode error')
        
        
        return new_two_seq, one_seqs