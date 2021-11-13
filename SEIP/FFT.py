from scipy.fftpack import fft,fftfreq
import numpy as np
class FFT(object):
    def __init__(self, top_k = 5):
        self.top_k = top_k
        
    def execute(self,str_one_ogl):
        fft_series = fft(str_one_ogl)
        power = np.abs(fft_series)
        sample_freq = fftfreq(fft_series.size)

        pos_mask = np.where(sample_freq>0)
        freqs = sample_freq[pos_mask]
        powers = power[pos_mask]

        top_k_seasons = self.top_k
        top_k_idxs = np.argpartition(powers, -top_k_seasons)[-top_k_seasons:]
        top_k_power = powers[top_k_idxs]
        fft_periods = (1 / freqs[top_k_idxs]).astype(int)
        fft_mask = np.where((fft_periods>=3)&(fft_periods<30))
        fft_list = fft_periods[fft_mask]
        fft_index = 0
        if len(fft_list)>1:    
            fft_index = fft_list[-1]
        elif len(fft_list) == 1:
            fft_index = fft_list[0]
        else:
            if len(fft_periods)>1:
                fft_index = fft_periods[-1]
            else:
                fft_index = fft_periods[0]
#         str_two = str_one_ogl[:fft_index]

        return fft_index
