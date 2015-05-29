# -*- coding: utf-8 -*-
"""
Created on Fri May 22 16:25:01 2015

@author: Felix Pfreundtner
"""

from __future__ import division, print_function, absolute_import
import math
from copy import deepcopy

import numpy as np
import scipy
from scipy.fftpack import rfft, irfft, fft, ifft
from scipy.signal import fftconvolve
import scipy.io.wavfile
import sys
import struct
import warnings



# @author: Felix Pfreundtner
def create_standard_dict(gui_dict):
    standard_dict=deepcopy(gui_dict)
    for sp in standard_dict:
        standard_dict[sp]=[]
    return standard_dict   
    
# @author: Felix Pfreundtner
# function does a normal school arithmetic round (Round half away from zero)
# different to pythons round() method (Round half to even)
def rnd(value):
    if value >=0:
       if  value-math.floor(value) < 0.5:
           value=math.floor(value)
       else:
           value=math.ceil(value)
    else:
       if  value-math.floor(value) <= 0.5:
           value=math.floor(value)
       else:
           value=math.ceil(value)
    return value    
    
# @author: Felix Pfreundtner
def get_block_param(output_bps, wave_param_common, hrtf_blocksize):
    # Standard FFT block size colculation dependend on output_fps
    fft_blocksize = 2**(round(math.log(wave_param_common[0]/output_bps, 2)))
    fft_blocktime = fft_blocksize/wave_param_common[0]
    sp_blocksize = fft_blocksize-hrtf_blocksize+1
    sp_blocktime = sp_blocksize/wave_param_common[0]
    overlap = (fft_blocksize-sp_blocksize)/fft_blocksize*100 # in %
    output_bps_real = 1/fft_blocktime
    
    return fft_blocksize, fft_blocktime, sp_blocksize, sp_blocktime, output_bps_real, overlap

# @author: Felix Pfreundtner
def initialize_wave_blockbeginend(standard_dict, sp_blocktime, wave_param_dict):
    wave_blockbeginend_dict=deepcopy(standard_dict) 
    for sp in wave_blockbeginend_dict:
        wave_blockbeginend_dict[sp]=[-(sp_blocktime*wave_param_dict[sp][1]),0]
    return wave_blockbeginend_dict
    
# @author: Felix Pfreundtner
def wave_blockbeginend(wave_blockbeginend_dict, wave_param_dict, sp_blocktime):   
    for sp in wave_blockbeginend_dict:
        wave_blockbeginend_dict[sp][0]=wave_blockbeginend_dict[sp][0] + (sp_blocktime*wave_param_dict[sp][1])
        wave_blockbeginend_dict[sp][1]=wave_blockbeginend_dict[sp][0] + (sp_blocktime*wave_param_dict[sp][1])
    return wave_blockbeginend_dict

# @author: Felix Pfreundtner
def get_hrtf_filenames(gui_dict_sp):   
    rounddifference = gui_dict_sp[0] % 5
    if rounddifference == 0:
        if gui_dict_sp[0] <= 180:
            azimuthangle = rnd(gui_dict_sp[0])
        else:
            azimuthangle = rnd(360 - gui_dict_sp[0])
    else:
        if gui_dict_sp[0] <= 180:
            if rounddifference < 2.5:
                azimuthangle = rnd(gui_dict_sp[0] - rounddifference) 
            else:
                azimuthangle = rnd(gui_dict_sp[0] + 5 - rounddifference)
        else:  
            if rounddifference < 2.5:
                azimuthangle = 360 - rnd(gui_dict_sp[0] - rounddifference)
            else:    
                azimuthangle = 360 - rnd(gui_dict_sp[0] + 5 - rounddifference)    
    hrtf_filenames_dict_sp = ["./kemar/compact/elev0/H0e"+str(azimuthangle).zfill(3)+"a.wav"]
    return hrtf_filenames_dict_sp

# @author: Felix Pfreundtner
def get_hrtf(hrtf_filenames_dict_sp, gui_dict_sp):
    for hrtf_filename in hrtf_filenames_dict_sp:
        _, hrtf_input = scipy.io.wavfile.read(hrtf_filename)
        if gui_dict_sp[0] <= 180:
            hrtf_block_dict_sp=hrtf_input
        else:
            hrtf_input[:,[0, 1]] = hrtf_input[:,[1, 0]]
            hrtf_block_dict_sp=hrtf_input  
    return hrtf_block_dict_sp    
    
# @author: Felix Pfreundtner
def get_sp_block_dict(signal_dict_sp, wave_blockbeginend_dict_sp, sp_blocksize, error_list_sp):    
    sp_block_dict_sp=signal_dict_sp[int(rnd(wave_blockbeginend_dict_sp[0])):int(rnd(wave_blockbeginend_dict_sp[1]))]
    # if last block of speaker input signal
    if len(sp_block_dict_sp) == sp_blocksize:
        error_list_sp.append("correct blocksize")
       
    elif len(sp_block_dict_sp) < sp_blocksize:
        error_list_sp.append("block smaller than correct blocksize")
        add_zeros_to_block = np.zeros((sp_blocksize-len(sp_block_dict_sp),),dtype='int16')
        sp_block_dict_sp = np.concatenate((sp_block_dict_sp, add_zeros_to_block))
    else:
        error_list_sp.append("error block size doesn't match")
    return sp_block_dict_sp, error_list_sp
    
# @author: Felix Pfreundtner
def fft_convolve(sp_block_sp, hrtf_block_sp_l_r, fft_blocksize):
    
    # Do for speaker sp zeropadding: zeropad hrtf (left or right input) and speaker (mono input)
    hrtf_zeros = np.zeros((fft_blocksize-len(hrtf_block_sp_l_r), ), dtype = 'int16')
    hrtf_block_sp_zeropadded = np.concatenate((hrtf_block_sp_l_r, hrtf_zeros))
    sp_zeros = np.zeros((fft_blocksize-len(sp_block_sp), ), dtype = 'int16')
    sp_block_sp_zeropadded = np.concatenate((sp_block_sp, sp_zeros))
    
    # bring time domain input to to frequency domain
    hrtf_block_sp_frequency = fft(hrtf_block_sp_zeropadded, fft_blocksize)
    sp_block_sp_frequency = fft(sp_block_sp_zeropadded, fft_blocksize)
    
    # execute convulotion of speaker input and hrtf input: multiply complex frequency domain vectors
    binaural_block_sp_frequency = sp_block_sp_frequency * hrtf_block_sp_frequency
    
    # bring multiplied spectrum back to time domain, disneglected small complex time parts resulting from numerical fft approach
    binaural_block_sp = ifft(binaural_block_sp_frequency, fft_blocksize).real
    
    return binaural_block_sp
    
# @author: Felix Pfreundtner
def apply_hamming_window(inputsignal):
    hamming_window = [0.53836 - 0.46164*math.cos(2*math.pi*t/(len(inputsignal) - 1)) for t in range(len(inputsignal))]
    hamming_window = np.asarray(hamming_window, dtype=np.float64)
    inputsignal = inputsignal * hamming_window
    return inputsignal
    

# @author: Felix Pfreundtner
def bit_int(binaural_dict):
    binaural_dict_scaled={}
    for sp in binaural_dict:
        binaural_dict_scaled[sp] = np.zeros((len(binaural_dict[sp]), 2), dtype=np.int16)
        for l_r in range(2):
            maximum_value=np.max(np.abs(binaural_dict[sp][:, l_r]))
            if maximum_value != 0:
                binaural_dict_scaled[sp][:, l_r] = binaural_dict[sp][:, l_r]/maximum_value * 32767
                binaural_dict_scaled[sp] = binaural_dict_scaled[sp].astype(np.int16, copy=False)
  
    return binaural_dict_scaled

# @author: Felix Pfreundtner
def add_to_binaural_dict(binaural_block_dict, binaural_dict, begin_block, outputsignal_sample_number):
    outputsignal_sample_number= len(binaural_dict)   
    binaural_dict[begin_block : outputsignal_sample_number, :] += binaural_block_dict[0 : (outputsignal_sample_number - begin_block), :]
    binaural_dict=np.concatenate((binaural_dict, binaural_block_dict[(outputsignal_sample_number - begin_block):, :]))
    outputsignal_sample_number= len(binaural_dict)
    
    return binaural_dict, outputsignal_sample_number

# @author: Felix Pfreundtner
def writebinauraloutput(binaural_dict_scaled, wave_param_common, gui_dict):
    for sp in binaural_dict_scaled:
        scipy.io.wavfile.write(gui_dict[sp][2] + "binauraloutput.wav" , wave_param_common[0], binaural_dict_scaled[sp])    

#Preparing for get_rate_and_data:
def _read_data_chunk(fid, comp, noc, bits, mmap=False):
    if _big_endian:
        fmt = '>i'
    else:
        fmt = '<i'
    size = struct.unpack(fmt,fid.read(4))[0]

    bytes = bits//8
    if bits == 8:
        dtype = 'u1'
    else:
        if _big_endian:
            dtype = '>'
        else:
            dtype = '<'
        if comp == 1:
            dtype += 'i%d' % bytes
        else:
            dtype += 'f%d' % bytes
    if not mmap:
        data = numpy.fromstring(fid.read(size), dtype=dtype)
    else:
        start = fid.tell()
        data = numpy.memmap(fid, dtype=dtype, mode='c', offset=start,
                            shape=(size//bytes,))
        fid.seek(start + size)

    if noc > 1:
        data = data.reshape(-1,noc)
    return data
    
#Preparing get_rate_and_data #2:
    
def _read_fmt_chunk(fid):
    if _big_endian:
        fmt = '>'
    else:
        fmt = '<'
    res = struct.unpack(fmt+'iHHIIHH',fid.read(20))
    size, comp, noc, rate, sbytes, ba, bits = res
    if comp not in KNOWN_WAVE_FORMATS or size > 16:
        comp = WAVE_FORMAT_PCM
        warnings.warn("Unknown wave file format", WavFileWarning)
        if size > 16:
            fid.read(size - 16)

    return size, comp, noc, rate, sbytes, ba, bits


#Preparing get_rate_and_data #3:
def _skip_unknown_chunk(fid):
    if _big_endian:
        fmt = '>i'
    else:
        fmt = '<i'

    data = fid.read(4)
    size = struct.unpack(fmt, data)[0]
    fid.seek(size, 1)

#Preparing get_rate_and_data #4:
def _read_riff_chunk(fid):
    global _big_endian
    str1 = fid.read(4)
    if str1 == b'RIFX':
        _big_endian = True
    elif str1 != b'RIFF':
        raise ValueError("Not a WAV file.")
    if _big_endian:
        fmt = '>I'
    else:
        fmt = '<I'
    fsize = struct.unpack(fmt, fid.read(4))[0] + 8
    str2 = fid.read(4)
    if (str2 != b'WAVE'):
        raise ValueError("Not a WAV file.")
    if str1 == b'RIFX':
        _big_endian = True
    return fsize


def get_rate_and_data(filename):
    '''filename: string or open file handle
    Input .wav file.'''
    
    if hasattr(filename,'read'):
        fid = filename
    else:
        fid = open(filename, 'rb')

    try:
        fsize = _read_riff_chunk(fid)
        noc = 1
        bits = 8
        comp = WAVE_FORMAT_PCM
        while (fid.tell() < fsize):
            # read the next chunk
            chunk_id = fid.read(4)
            if chunk_id == b'fmt':
                size, comp, noc, rate, sbytes, ba, bits = _read_fmt_chunk(fid)
            elif chunk_id == b'fact':
                _skip_unknown_chunk(fid)
            elif chunk_id == b'data':
                data = _read_data_chunk(fid, comp, noc, bits)
            elif chunk_id == b'LIST':
                # Someday this could be handled properly but for now skip it
                _skip_unknown_chunk(fid)
            else:
                warnings.warn("Chunk (non-data) not understood, skipping it.",
                              WavFileWarning)
                _skip_unknown_chunk(fid)
    finally:
        if not hasattr(filename,'read'):
            fid.close()
        else:
            fid.seek(0)

    return rate, data
    ''' The returned sample rate is a Python integer
    * The data is returned as a numpy array with a
      data-type determined from the file.'''
    