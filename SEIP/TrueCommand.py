from utils import *
import re


def s7type(str1):
    strlist = strpreprocess(str1, "bytelist")
    if strlist[5] == 'e0':
        return 'CR_TPDU'
    elif strlist[5] == 'd0':
        return 'CC_TPDU'
    elif strlist[5] == 'f0':
        if strlist[3] == '07':
            return 'DT_TPDU'
        else:
            try:
                if strlist[8] == '01' and strlist[17] == '04':
                    return 'Job_Read_Var'
                if strlist[8] == '03' and strlist[19] == '04':
                    return 'Ack_Data_Read_Var'
                if strlist[8] == '01' and strlist[17] == '05':
                    return 'Job_Write_Var'
                if strlist[8] == '03' and strlist[19] == '05':
                    return 'Ack_Data_Write_Var'
                if strlist[8] == '01' and strlist[17] == '1a':
                    return 'Job_Reqest_download'
                if strlist[8] == '03' and strlist[19] == '1a':
                    return 'Ack_Data_Reqest_download'
                if strlist[8] == '01' and strlist[17] == '1b':
                    return 'Job_Download_block'
                if strlist[8] == '03' and strlist[19] == '1b':
                    return 'Ack_Data_Download_block'
                if strlist[8] == '01' and strlist[17] == '1c':
                    return 'Job_Download_ended'
                if strlist[8] == '03' and strlist[19] == '1c':
                    return 'Ack_Data_Download_ended'
                if strlist[8] == '01' and strlist[17] == '1d':
                    return 'Job_Start_upload'
                if strlist[8] == '03' and strlist[19] == '1d':
                    return 'Ack_Data_Start_upload'
                if strlist[8] == '01' and strlist[17] == '1e':
                    return 'Job_Upload'
                if strlist[8] == '03' and strlist[19] == '1e':
                    return 'Ack_Data_Upload'
                if strlist[8] == '01' and strlist[17] == '1f':
                    return 'Job_End_upload'
                if strlist[8] == '03' and strlist[19] == '1f':
                    return 'Ack_Data_End_upload'
                if strlist[8] == '01' and strlist[17] == '28':
                    return 'Job_PI-Service'
                if strlist[8] == '03' and strlist[19] == '28':
                    return 'Ack_Data_PI-Service'
                if strlist[8] == '01' and strlist[17] == '29':
                    return 'Job_PLC_Stop'
                if strlist[8] == '03' and strlist[19] == '29':
                    return 'Ack_Data_PLC_Stop'
                if strlist[8] == '01' and strlist[17] == 'f0':
                    return 'Job_Setup_communication'
                if strlist[8] == '03' and strlist[19] == 'f0':
                    return 'Ack_Data_Setup_communication'
                if strlist[22] == '42' and strlist[23] == '01':
                    return 'Request_Cyclic_data_Memory'
                if strlist[22] == '82' and strlist[23] == '01':
                    return 'Response_Cyclic_data_Memory'
                if strlist[22] == '42' and strlist[23] == '05':
                    return 'Request_Cyclic_data_Memory2'
                if strlist[22] == '82' and strlist[23] == '05':
                    return 'Response_Cyclic_data_Memory2'
                if strlist[22] == '43' and strlist[23] == '01':
                    return 'Request_Block_function_List_blocks'
                if strlist[22] == '83' and strlist[23] == '01':
                    return 'Response_Block_function_List_blocks'
                if strlist[22] == '43' and strlist[23] == '02':
                    return 'Request_Block_function_List_blocks_of_type'
                if strlist[22] == '83' and strlist[23] == '02':
                    return 'Response_Block_function_List_blocks_of_type'
                if strlist[22] == '43' and strlist[23] == '03':
                    return 'Request_Block_function_Get_block_info'
                if strlist[22] == '83' and strlist[23] == '03':
                    return 'Response_Block_function_Get_block_info'
                if strlist[22] == '44' and strlist[23] == '01':
                    return 'Request_CPU_function_Read_SZL'
                if strlist[22] == '84' and strlist[23] == '01':
                    return 'Response_CPU_function_Read_SZL'
                if strlist[22] == '47' and strlist[23] == '01':
                    return 'Request_Time_functions_Read_clock'
                if strlist[22] == '87' and strlist[23] == '01':
                    return 'Response_Time_functions_Read_clock'
                if strlist[22] == '47' and strlist[23] == '02':
                    return 'Request_Time_functions_Set_clock'
                if strlist[22] == '87' and strlist[23] == '02':
                    return 'Response_Time_functions_Set_clock'
            except:
                return 'error'
    else:
        return 'wrong'