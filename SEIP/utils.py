import numpy as np
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count
import pandas as pd
import dpkt
import struct
import sys,os
import socket
import time
import random
import math
import re
from netzob.all import *
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import adjusted_mutual_info_score, normalized_mutual_info_score
from sklearn import metrics
from sklearn.metrics import fowlkes_mallows_score

def ClusterScore(clusterstrue,clustersfinal):
    
    ari = adjusted_rand_score(clusterstrue,clustersfinal)
    print('ari: ',ari)
    print('------------------')


    ami = adjusted_mutual_info_score(clusterstrue,clustersfinal,average_method='arithmetic')
    print('ami: ', ami)
    print('------------------')
    
    nmi = normalized_mutual_info_score(clusterstrue,clustersfinal,average_method='arithmetic')
    print('nmi: ', nmi)
    print('------------------')
    
    h_score = metrics.homogeneity_score(clusterstrue,clustersfinal)
    c_score = metrics.completeness_score(clusterstrue,clustersfinal)
    v_measure = metrics.v_measure_score(clusterstrue,clustersfinal)
    print('h_score: ',h_score)
    print('c_score: ',c_score)
    print('v_measure: ',v_measure)
    print('------------------')

    fmi = fowlkes_mallows_score(clusterstrue,clustersfinal)
    print('fmi: ',fmi)
    score = (ari,ami,nmi,h_score,c_score,v_measure,fmi)
    return score

def Coding(label):
    keys = {}
    t = 0 
    for i in range(len(label)):
        if label[i] not in keys:
            keys.update({label[i]:t})
            t+=1
    Codinglabel = []
    for i in range(len(label)):
        Codinglabel.append(keys[label[i]])
    return Codinglabel

def filepreprocess(file):
    if file.split('.')[-1] == 'pcap':
        messages = PCAPImporter.readFile(file, importLayer = 5).values()
        data = [messages[i].data.hex() for i in range(len(messages))]
        return data
    elif file.split('.')[-1] == 'txt':
        messages = FileImporter.readFile(file).values()
        data = [bytes.decode(messages[i].data) for i in range(len(messages))]
        return data
    else:
        return 'error'

        

def strpreprocess(str1,flag):
    if flag == 'str':
        if type(str1) == str or type(str1) == np.str_:
            return str1
        elif type(str1) == list or type(str1) == np.ndarray:
            if type(str1[0]) == str or type(str1[0]) == np.str_:
                return ''.join(str1)
            elif type(str1[0]) == int or type(str1[0]) == np.int64:
                str1 = ['{:02x}'.format(str1[i]) for i in range(len(str1))]
                return ''.join(str1)
            else:
                return 'wrong00'
        else:
            return 'wrong01'
    elif flag == 'bytelist':
        if type(str1) == str or type(str1) == np.str_:
            str1 = re.findall(r'.{2}', str1)
            return str1
        elif type(str1) == list or type(str1) == np.ndarray:
            if type(str1[0]) == str or type(str1[0]) == np.str_:
                return str1
            elif type(str1[0]) == int or type(str1[0]) == np.int64:
                str1 = ['{:02x}'.format(str1[i]) for i in range(len(str1))]
                return str1
            else:
                return 'wrong10'
        else:
            return 'wrong11'
    elif flag == 'intlist':
        if type(str1) == str or type(str1) == np.str_:
            str1 = re.findall(r'.{2}', str1)
            str1 = [int(str1[i],16) for i in range(len(str1))]
            return str1
        elif type(str1) == list or type(str1) == np.ndarray:
            if type(str1[0]) == str or type(str1[0]) == np.str_:
                str1 = [int(str1[i],16) for i in range(len(str1))]
                return str1
            elif type(str1[0]) == int or type(str1[0]) == np.int64:
                return str1
            else:
                return 'wrong20'
        else:
            return 'wrong21'
    else:
        return 'wrong'

def sigmoid(x):
    return 1/(1+np.exp(-x))

def tanh(x):
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))

def worker(input, output):
    for func, args, serial in iter(input.get, 'STOP'):
        result = calculate(func, args, serial)
        output.put(result)

def calculate(func, args, serial):
    result = func(*args)
    return (result, serial)

def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return False
    

def tcp_pcap2app(pcap_name):
    f = open(pcap_name,'rb')

    pcap = dpkt.pcap.Reader(f)
    dic= {}
    application_data = []
    mode = []
    for ts,buf in pcap:
        
        eth=dpkt.ethernet.Ethernet(buf)
    #     print(eth.type)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        ip=eth.data
        ip_src = inet_to_str(ip.src)
        ip_dst = inet_to_str(ip.dst)
        if ip.p == 6:
            tcp = ip.data
            tcp_src = tcp.sport
            tcp_dst = tcp.dport

            if tcp_src == 502 or tcp_dst == 502:
                mode.append('MODBUS')
            elif tcp_src == 102 or tcp_dst == 102:
                mode.append('S7COMM')
            elif tcp_src == 44818 or tcp_dst == 44818:
                mode.append('CIP')
            else:
                mode.append('None')
        #     print(tcp)
            payload = tcp.data
            if payload == b'':
                continue
            temp = payload.hex()
            #payload
            if temp in dic:
                continue
            else:
                dic.update({temp:1})

            application_data.append(payload.hex())
    
    return mode, application_data





def isASCII(byte):
    if int(byte,16) >= 32 and int(byte,16) <= 127:
        return True

def ContinueASCII(str1,pos):
    tstr = strpreprocess(str1,'bytelist')
    tempstr = tstr[pos:]
    i = 0
    poses = []
    while(i<len(tempstr)):
        if isASCII(tempstr[i]):
            j = i+1
            while(j<len(tempstr)):
                if not isASCII(tempstr[j]):
                    break
                j+=1
            if j-i>=3:
                poses.append([i,j])
            i = j
        i+=1
    
    if len(poses) == 0:
        return str1
    
    finalstr = list(tstr[:pos])
    if poses[0][0] > 0:
        finalstr += list(tempstr[:poses[0][0]])
        
    Text = ['30','30','30']
    for k in range(len(poses)):
        finalstr += Text
        if k == len(poses) - 1:
            finalstr += list(tempstr[poses[k][1]:])
        else:
            finalstr += list(tempstr[poses[k][1]:poses[k+1][0]])
            
    return finalstr

def isPadding(byte):
    if int(byte,16) == 0:
        return True

def ContinuePadding(str1,pos):
    tstr = strpreprocess(str1,'bytelist')
    tempstr = tstr[pos:]
    i = 0
    poses = []
    while(i<len(tempstr)):
        if isPadding(tempstr[i]):
            j = i+1
            while(j<len(tempstr)):
                if not isPadding(tempstr[j]):
                    break
                j+=1
            if j-i>=3:
                poses.append([i,j])
            i = j
        i+=1
    
    if len(poses) == 0:
        return str1
        
    finalstr = list(tstr[:pos])
    if poses[0][0] > 0:
        finalstr += list(tempstr[:poses[0][0]])
        
    Text = ['00','00','00']
    for k in range(len(poses)):
        finalstr += Text
        if k == len(poses) - 1:
            finalstr += list(tempstr[poses[k][1]:])
        else:
            finalstr += list(tempstr[poses[k][1]:poses[k+1][0]])
            
    return finalstr

def ContinueValue(str1,pos):
    tstr = strpreprocess(str1,'bytelist')
    tempstr = tstr[pos:]
    i = 0
    poses = []
    while(i<len(tempstr)):
        j = i+1
        while(j<len(tempstr)):
            if tempstr[j] != tempstr[i]:
                break
            j+=1
        if j-i>=3:
            poses.append([i,j,tempstr[i]])
        i = j        
        i+=1

    if len(poses) == 0:
        return str1        
        
    finalstr = list(tstr[:pos])
    if poses[0][0] > 0:
        finalstr += list(tempstr[:poses[0][0]])
        
    for k in range(len(poses)):
        finalstr += [poses[k][2] for kk in range(3)]
        if k == len(poses) - 1:
            finalstr += list(tempstr[poses[k][1]:])
        else:
            finalstr += list(tempstr[poses[k][1]:poses[k+1][0]])
            
    return finalstr

def ContinueRegister(str1,pos):
    tstr = strpreprocess(str1,'bytelist')
    tempstr = tstr[pos:]
    i = 0
    poses = []
    while(i<len(tempstr)):
        j = i+2
        while(j<len(tempstr)-1):
            if tempstr[j] != tempstr[i] or tempstr[j+1] != tempstr[i+1]:
                break
            j+=2
        if j-i>=4:
            poses.append([i,j,tempstr[i],tempstr[i+1]])
        i = j        
        i+=1
        
    if len(poses) == 0:
        return str1 
        
    finalstr = list(tstr[:pos])
    if poses[0][0] > 0:
        finalstr += list(tempstr[:poses[0][0]])
        
    for k in range(len(poses)):
        finalstr += [poses[k][2],poses[k][3]]
        if k == len(poses) - 1:
            finalstr += list(tempstr[poses[k][1]:])
        else:
            finalstr += list(tempstr[poses[k][1]:poses[k+1][0]])
            
    return finalstr


def FrequenctBytes(messages):
    dataset = []
    for i in range(len(messages)):
        dataset.append(strpreprocess(messages[i],'intlist'))
    
    freq_list = np.zeros(256)
    for i in range(len(dataset)):
        for j in dataset[i]:
            freq_list[j] += 1
    
    freq_sort = np.argsort(freq_list)[::-1]
    
    freq_key = {}
    for i in range(len(freq_list)):
        freq_key.update({'{:0>2x}'.format(freq_sort[i]):freq_list[freq_sort[i]]})
        
    for key in list(freq_key.keys()):
        if freq_key[key] == 0.0:
            del freq_key[key]
            
    keys = list(freq_key.keys())
    quad = int(.25*len(keys))
    
    quad1 = quad
    quad2 = quad
    dis1 = 0
    dis2 = 0
    quadflag = 0 
    while(dis1 == dis2):
        temp1 = quad1
        while(temp1>=0):
            if freq_key[keys[temp1]] == freq_key[keys[quad1]]:
                temp1 -= 1
                continue
            else:
                dis1 = abs(freq_key[keys[temp1]] - freq_key[keys[quad1]])
                quad1 = temp1
                break
    #     print('quad1:',quad1)
        temp2 = quad2
        while(temp2<len(keys)):
            if freq_key[keys[temp2]] == freq_key[keys[quad2]]:
                temp2 += 1
                continue
            else:
                dis2 = abs(freq_key[keys[temp2]] - freq_key[keys[quad2]])
                quad2 = temp2
                break
    #     print('quad2:',quad2)

        if quad1<0 or quad2>=len(keys):
            quadflag = 1
            break

    upEntropy = {}
    if quadflag == 0:    
        if dis1 > dis2:
            for k in keys[:quad1+1]:
                upEntropy[k] = freq_key[k]
        else:
            for k in keys[:quad2]:
                upEntropy[k] = freq_key[k]
    else:
        for k in keys[:quad]:
            upEntropy[k] = freq_key[k]
    
    return upEntropy

def isUnEntropy(byte, upEntropy):
    if byte not in upEntropy:
        return True
    
def ContinueRandom(str1, pos, upEntropy):
    tstr = strpreprocess(str1,'bytelist')
    tempstr = tstr[pos:]
    
    i = 0
    poses = []
    while(i<len(tempstr)):
        if isUnEntropy(tempstr[i],upEntropy):
            j = i+1
            while(j<len(tempstr)):
                if not isUnEntropy(tempstr[j],upEntropy):
                    break
                j+=1
            if j-i>=3:
                poses.append([i,j])
            i = j
        i+=1
    
    if len(poses) == 0:
        return str1
    
    finalstr = list(tstr[:pos])
    if poses[0][0] > 0:
        finalstr += list(tempstr[:poses[0][0]])
        
    Text = ['bf','bf','bf']
    for k in range(len(poses)):
        finalstr += Text
        if k == len(poses) - 1:
            finalstr += list(tempstr[poses[k][1]:])
        else:
            finalstr += list(tempstr[poses[k][1]:poses[k+1][0]])
            
    return finalstr

def PayloadProcess(str1, pos, upEntropy):
    tempstr = ContinuePadding(str1,pos)
    tempstr = ContinueValue(tempstr,pos)
    tempstr = ContinueASCII(tempstr,pos)
    tempstr = ContinueRandom(tempstr, pos, upEntropy)
    tempstr = ContinueRegister(tempstr,pos)
    return tempstr