# -*- coding: utf-8 -*-
"""
Created on Fri May 22 16:27:57 2015

@author: Felix Pfreundtner
"""

import algorithm_functions as alf


#manuell eingegebene Werte, da noch kein Mockup verfügbar
gui_dict={0: [272,1,"./audio/electrical_guitar_(44.1,16).wav"],
          1: [192.45,1,"./audio/sine_1kHz_(44.1,16).wav"]
         }
         
wave_param_dict={0: [970200, 44100,16],
                 1: [220500, 44100,16]
                } 
         
            
#Initialize FFT iteration after GUI call
        
#Standard samplerate, sampledepth, output_frames_per_second         
wave_param_common = [44100,16]  
standard_dict=alf.create_standard_dict(gui_dict)
output_fps = 60  
#Overlap FFT in Prozent
overlap=0
              
iterationcounter = 0
fft_blocksize, fft_blocktime, output_fps_real = alf.set_fft_param(output_fps, wave_param_common)
wave_blockbeginend_dict = alf.initialze_wave_blockbeginend(standard_dict, overlap, fft_blocktime, wave_param_dict)


# Run FFT iteration  

# range of frames to be read in iteration from wav files (float numbers needed for adding the correct framesizes to the next iteration)               
# @matthias: for reading the wave file from sample a to b you need to round the constraints from wave_blockbeginend_dict{sp#,[ a, b]: -> int(alf.normal_round(a)) and int(alf.normal_round(b))
wave_blockbeginend_dict = alf.wave_blockbeginend(wave_blockbeginend_dict, wave_param_dict, fft_blocktime, overlap)

hrtf_filenames_dict = alf.get_hrtf_filenames(standard_dict, gui_dict)
hrtf_dict = alf.get_hrtf(hrtf_filenames_dict, standard_dict, gui_dict)

iterationcounter+=1



          