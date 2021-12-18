from utils import *
from ACF import ACF
from statsmodels.tsa.stattools import acf
from NW import NW
from DTW import DTW
from Iteration import Iteration

class SubMsg:
    def __init__(self, executor='NW', thred = 0.6, precent = .99):
                
        if executor == 'NW':
            nw = NW()
            self.executor = nw
        elif executor == 'DTW':
            dtw = DTW()
            self.executor = dtw
        else:
            return 'error'
        
        self.acf = ACF()
        self.itera = Iteration(executor = self.executor)
        self.newMsg = None
        self.template = None
        self.tmatrix = None
        self.thred = thred
        self.precent = precent
        
        
    def GetMidTmatrix(self, data):    
        tmatrix = np.zeros([len(data),len(data)])
        
        for x in range(len(data)-6):
            for y in range(x+6,len(data)):
                tacf = acf(np.array(data[x:y]),nlags=int(y-x-1),fft=False)
                tmatrix[x][y] = max(tacf[2:])

        if np.nanmax(tmatrix) >= self.thred:
            maxx = 0
            maxy = 0
            maxval = 0
            maxt = np.nanmax(tmatrix)
            for x in range(len(data)-6):
                for y in range(x+6,len(data)):
                    if tmatrix[x][y] < maxt* self.precent:
                        continue
                    else:
                        if tmatrix[x][y] * (y-x) > maxval:
                            maxval = tmatrix[x][y] *(y-x)
                            maxx = x
                            maxy = y
                
            return (maxx,maxy,tmatrix[maxx][maxy])
        else:
            return False
    
    

    def execute_mid(self,message):
        
        data = np.array(strpreprocess(message,'intlist'))
        
        tmatrixtuple = self.GetMidTmatrix(data)
        print(tmatrixtuple)
        if tmatrixtuple == False:
            return False
        
        tdata = list(data[tmatrixtuple[0]:tmatrixtuple[1]])
        
        if tdata.count(0) > .9 * len(tdata):
            return False
            
        ttwo = self.acf.execute(tdata)
        if ttwo > 0 and ttwo < len(tdata):
            iterations, final_pos, one_seqs, new_two_seq, final_score = self.itera.execute(tdata,tdata[:ttwo])
            if len(final_pos) > 2:
                
                self.newMsg = list(strpreprocess(data[:tmatrixtuple[0]],'bytelist')) + \
                list(strpreprocess(new_two_seq,'bytelist')) + list(strpreprocess(data[:tmatrixtuple[1]],'bytelist'))
                self.template = new_two_seq
                self.tmatrix = tmatrixtuple
                return True
            else:
                return False
        else:
            return False

    def GetRearTmatrix(self, data):    
        tmatrix = np.zeros(len(data))
        
        for x in range(len(data)-6):
            tacf = acf(np.array(data[x:]),nlags=int(len(data)-x-1),fft=False)
            tmatrix[x] = max(tacf[2:])

        if np.nanmax(tmatrix) >= self.thred:
            maxx = 0
            maxval = 0
            maxt = np.nanmax(tmatrix)
            for x in range(len(data)-6):
                if tmatrix[x] < maxt* self.precent:
                    continue
                else:
                    maxx = x
                    break    
            return (maxx,tmatrix[maxx])
        else:
            return False
        
        
    def execute_rear(self,message):
        
        data = np.array(strpreprocess(message,'intlist'))
        
        tmatrixtuple = self.GetRearTmatrix(data)
        
        if tmatrixtuple == False:
            return False
        
        tdata = list(data[tmatrixtuple[0]:])
        
        #if tdata.count(0) > .9 * len(tdata):
            #return False
            
        ttwo = self.acf.execute(tdata)
        if ttwo > 0 and ttwo < len(tdata):
            iterations, final_pos, one_seqs, new_two_seq, final_score = self.itera.execute(tdata,tdata[:ttwo])
            if len(final_pos) > 2:
                
                self.newMsg = list(strpreprocess(data[:tmatrixtuple[0]],'bytelist')) + \
                list(strpreprocess(new_two_seq,'bytelist'))
                self.template = new_two_seq
                self.tmatrix = tmatrixtuple
                return True
            else:
                return False
        else:
            return False
        
        
    def execute_pos(self,message,pos):
        
        data = np.array(strpreprocess(message,'intlist'))
        
        if pos > len(data) - 6:
            return False
        
        tdata = list(data[pos:])
        
        if tdata.count(0) > .9 * len(tdata):
            return False
            
        ttwo = self.acf.execute(tdata)
        if ttwo > 0 and ttwo < len(tdata):
            iterations, final_pos, one_seqs, new_two_seq, final_score = self.itera.execute(tdata,tdata[:ttwo])
            if len(final_pos) > 2:
                
                self.newMsg = list(strpreprocess(data[:pos],'bytelist')) + \
                list(strpreprocess(new_two_seq,'bytelist'))
                self.template = new_two_seq
                return True
            else:
                return False
        else:
            return False
        
