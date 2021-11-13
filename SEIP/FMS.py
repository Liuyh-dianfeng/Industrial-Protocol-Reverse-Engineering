import math
import numpy as np
def FMS(data_true,data_neme):
    FMS_list = []
    for i in range(len(data_neme)):
        temp_infer = data_neme[i][1:-1]
#         print(temp_infer)
        temp_true = data_true[i]
#         print(temp_true)
        R = len(data_true[i])-2
        I = len(data_neme[i])-2
        deltas = []
        for k in range(1,len(temp_true)-1):
            delta_list = []
            for j in range(len(temp_infer)):
                if temp_true[k-1] + (temp_true[k] - temp_true[k-1])/2 <=  temp_infer[j] and temp_true[k] + (temp_true[k+1] - temp_true[k])/2 >=  temp_infer[j]:
                    delta_list.append(temp_infer[j])
#             print('delta_list:',delta_list)
            delta = np.nan
            if len(delta_list)>0:
                delta = min([abs(delta_list[p] - temp_true[k]) for p in range(len(delta_list))])
#             print('delta:',delta)
            deltas.append(delta)
        matchgain=[]
        for j in range(len(deltas)):
            if np.isnan(deltas[j]):
                continue
            else:
                matchgain.append(math.exp(-(deltas[j]/2)**2))
    #     print(matchgain)
        FMS_list.append(math.exp(-((R-I)/R)**2)/R*sum(matchgain))
#         break
    return FMS_list