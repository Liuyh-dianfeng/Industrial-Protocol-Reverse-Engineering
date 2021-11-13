from utils import *
import re
import pyshark
import nest_asyncio

class HeaderInfer(object):
    
    def __init__(self,mode='real'):
        self.mode = mode
        
        
    def execute(self,pcapfile):
        
        pmode, app_data = tcp_pcap2app(pcapfile)
        
        if self.mode == 'real':
            underlayer_len = 54
            dataset = []
            
            app_databyte = [re.findall(r'.{2}',app_data[i]) for i in range(len(app_data))]
            
            nest_asyncio.apply()
            pcap = pyshark.FileCapture(pcapfile)
            pcap.load_packets()
            if len(pcap) == 0:
                print('load error!')
                return
            for i in range(len(pcap)):
                if pcap[i].highest_layer != pmode[i]:
                    print('mode error!',pcap[i].highest_layer,pmode[i])
                    return
                if pcap[i].highest_layer == 'CIP':
                    dataset.append(app_databyte[i][int(app_databyte[i][int(pcap[i].cip.msp_num_services.pos)-underlayer_len],16)*2 + 2 + int(pcap[i].cip.msp_num_services.pos)-underlayer_len:])
                elif pcap[i].highest_layer == 'MODBUS':
                    dataset.append(app_databyte[i][int(pcap[i].modbus.byte_cnt.pos)- underlayer_len + 1:])
                elif pcap[i].highest_layer == 'S7COMM':
                    try:
                        dataset.append(app_databyte[i][int(pcap[i].s7comm.cyclic_interval_time.pos)-underlayer_len + 1:])
                    except:
                        dataset.append(app_databyte[i][int(pcap[i].s7comm.param_itemcount.pos)-underlayer_len + 1:])
                else:
                    print('unknow mode!')
                    return
            return dataset
        
        else:
            min_len = len(app_data[0])

            for i in range(len(app_data)):
                if len(app_data[i]) < min_len:
                    min_len = len(app_data[i])

            header_temp = [app_data[i][:min_len] for i in range(len(app_data))]


            # n-grams = 4
            ngrams4 = [header_temp[i:i+8] for i in range(len(header_temp))]
            ngrams4_val = [int(ngrams4[i],16) for i in range(len(n_grams4))]
        
    
