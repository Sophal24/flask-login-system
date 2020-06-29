import os
from pocketsphinx import AudioFile


config = {
    'verbose' : False,
    'logfn' : '/dev/null' or 'nul',
    'audio_file' : 'tovmok.wav',
    'audio_device' : None,
    'sampling_rate' : 16000,
    'buffer_size' : 2048,
    'no_search' : False,
    'full_utt' : False,
    'hmm' : 'model_parameters/iot.ci_cont',
    'lm' : 'etc/iot.lm.DMP',
    'dict' : 'etc/iot.dic',
}

audio = AudioFile(**config)
for phrase in audio:
    print(phrase)
