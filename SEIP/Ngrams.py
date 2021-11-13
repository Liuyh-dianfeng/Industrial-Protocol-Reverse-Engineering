import numpy as np
import re
import random
import math
from scipy import optimize
from minepy import MINE

class FieldType():
    def __init__(self):
        self.pos = (-1,-1)
        self.ngrams = 0
        self.bigRelation = []
        self.littleRelation = []
        self.bigEnd = []
        self.littleEnd = []
        self.originList = []
        self.entropy = -1
        

def Ngrams(header_temp,nlist=[1,2,3,4]):
    fieldTypes ={}
    for n in nlist:
        fieldTypes.update({n:[]})
        ngrams = np.array([[header_temp[i][j:j+n*2] for j in range(0,len(header_temp[i])-n*2+1,2)] \
                           for i in range(len(header_temp))])

        ngrams_big = np.array([[int(ngrams[i][j],16) for j in range(len(ngrams[i]))] for i in range(len(ngrams))])

        ngrams_little = np.array([[int(''.join(re.findall(r'.{2}',ngrams[i][j])[::-1]),16) \
                                   for j in range(len(ngrams[i]))] for i in range(len(ngrams))])
    
        fieldTypes[n] = np.array([FieldType() for i in range(len(ngrams[0]))])

        for i in range(len(fieldTypes[n])):
            fieldTypes[n][i].pos = (i,i+n-1)
            fieldTypes[n][i].ngrams = n
            fieldTypes[n][i].originList = [ngrams[j][i] for j in range(len(ngrams))]
            fieldTypes[n][i].bigEnd = [ngrams_big[j][i] for j in range(len(ngrams_big))]
            fieldTypes[n][i].littleEnd = [ngrams_little[j][i] for j in range(len(ngrams_little))]
    
    return fieldTypes

class CorrelationFind():
    def __init__(self,acc=-9,LowerK=0.124,UpperK=100,LowerB=-257,UpperB=256):
        self._acc = acc
        self._LowerK = LowerK
        self._UpperK = UpperK
        self._LowerB = LowerB
        self._UpperB = UpperB
    @property
    def acc(self):
        return self._acc
    @property
    def LowerK(self):
        return self._LowerK
    @property
    def UpperK(self):
        return self._UpperK
    @property
    def LowerB(self):
        return self._LowerB
    @property
    def UpperB(self):
        return self._UpperB
    
    
    
    def executor(self,list1,list2,acc=None):
        if acc==None:
            acc = self.acc
        small_len =len(list1) if len(list1)< len(list2) else len(list2)
        if small_len < 3:
            return 'no'
        tlist = random.sample(range(small_len),3)
        cor = np.corrcoef([list1[j] for j in tlist],[list2[j] for j in tlist])[0][1]
        if cor > 1.0-10**acc:
            cor = np.corrcoef(list1[:small_len],list2[:small_len])[0][1]
        else:
            return 'no'
        
        from scipy import optimize
        def corr(x, K, B):
            return K * x + B
        if cor > 1.0-10**acc:
            K, B = optimize.curve_fit(corr,list1[:small_len],list2[:small_len])[0] #list2 = K * list1 + B
            if K<self.LowerK or K> self.UpperK or B<self.LowerB or B>self.UpperB:
                return 'no'
            else:
                return (round(K,3),round(B,3)) 
        else:
            return 'no'

def FindFieldType(fieldTypes,Lengths,MicFlag = 0):
    mic_thredshold = 0.8
    corFind = CorrelationFind()
    mine = MINE()
    for n in fieldTypes:
        for i in range(len(fieldTypes[n])):
            if len(set(fieldTypes[n][i].bigEnd)) == 1:
                fieldTypes[n][i].bigRelation.append(('Fix',fieldTypes[n][i].bigEnd[0]))
                fieldTypes[n][i].littleRelation.append(('Fix',fieldTypes[n][i].littleEnd[0]))
                
            else:
                len_big = corFind.executor(fieldTypes[n][i].bigEnd,Lengths,acc=n*-3)
                len_little = corFind.executor(fieldTypes[n][i].littleEnd,Lengths,acc=n*-3)
                if len_big != 'no':
                    fieldTypes[n][i].bigRelation.append(('Len',len_big[0],len_big[1]))
                if len_little != 'no':
                    fieldTypes[n][i].littleRelation.append(('Len',len_little[0],len_little[1]))

                for m in fieldTypes:
                    for j in range(len(fieldTypes[m])):
                        
                        if (j in range(i,i+n)) or (i in range(j,j+m)):
                            continue
                        else:
                            
                            cor_bigbig = corFind.executor(fieldTypes[n][i].bigEnd,\
                                                          fieldTypes[m][j].bigEnd,acc=int((n+m)/2)*-3)
                            cor_biglittle = corFind.executor(fieldTypes[n][i].bigEnd,\
                                                             fieldTypes[m][j].littleEnd,acc=int((n+m)/2)*-3)
                            cor_littlebig = corFind.executor(fieldTypes[n][i].littleEnd,\
                                                              fieldTypes[m][j].bigEnd,acc=int((n+m)/2)*-3)
                            cor_littlelittle = corFind.executor(fieldTypes[n][i].littleEnd,\
                                                                 fieldTypes[m][j].littleEnd,acc=int((n+m)/2)*-3)
                            
                            if cor_bigbig != 'no':
                                fieldTypes[n][i].bigRelation.append(('Cor',cor_bigbig[0],cor_bigbig[1],\
                                                                     fieldTypes[m][j].pos))
                            if cor_biglittle != 'no' and m!=1:
                                fieldTypes[n][i].bigRelation.append(('Cor',cor_biglittle[0],\
                                                                     cor_biglittle[1],fieldTypes[m][j].pos[::-1]))
                            if cor_littlebig != 'no' and n!=1:
                                fieldTypes[n][i].littleRelation.append(('Cor',cor_littlebig[0],\
                                                                        cor_littlebig[1],fieldTypes[m][j].pos))
                            
                            if cor_littlelittle != 'no' and m!=1 and n!=1:
                                fieldTypes[n][i].littleRelation.append(('Cor',cor_littlelittle[0],\
                                                                       cor_littlelittle[1],fieldTypes[m][j].pos[::-1]))
                                
                            if MicFlag != 0:    
                                mine.compute_score(fieldTypes[n][i].bigEnd,fieldTypes[m][j].bigEnd)
                                mic_bigbig = mine.mic()
                                if mic_bigbig > mic_thredshold:
                                    fieldTypes[n][i].bigRelation.append(('Mic',mic_bigbig,\
                                                                         fieldTypes[m][j].pos))
                                mine.compute_score(fieldTypes[n][i].bigEnd,fieldTypes[m][j].littleEnd)
                                mic_biglittle = mine.mic()
                                if mic_biglittle > mic_thredshold and m!=1:
                                    fieldTypes[n][i].bigRelation.append(('Mic',mic_biglittle,\
                                                                         fieldTypes[m][j].pos[::-1]))
                                mine.compute_score(fieldTypes[n][i].littleEnd,fieldTypes[m][j].bigEnd)
                                mic_littlebig = mine.mic()
                                if mic_littlebig > mic_thredshold and n!=1:
                                    fieldTypes[n][i].littleRelation.append(('Mic',mic_littlebig,\
                                                                         fieldTypes[m][j].pos))
                                mine.compute_score(fieldTypes[n][i].littleEnd,fieldTypes[m][j].littleEnd)
                                mic_littlelittle = mine.mic()
                                if mic_littlelittle > mic_thredshold and m!=1 and n!=1:
                                    fieldTypes[n][i].littleRelation.append(('Mic',mic_littlelittle,\
                                                                         fieldTypes[m][j].pos[::-1]))

            
    return fieldTypes

def EntropyCalcu(List):
    result=-1;
    
    if(len(List)>0) and (round(sum(List),1)==1):
        result=0;
    else:
        return result
    
    for x in List:
        result+=(-x)*math.log(x,2)
    return result;

def FindFieldEntropy(fieldTypes):
    for n in fieldTypes:
        for i in range(len(fieldTypes[n])):
            bigSet = set(fieldTypes[n][i].bigEnd)
            bigSetList= []
            for s in bigSet:
                bigSetList.append(list(fieldTypes[n][i].bigEnd).count(s)/len(fieldTypes[n][i].bigEnd))
            fieldTypes[n][i].entropy = EntropyCalcu(bigSetList)
            
    return fieldTypes