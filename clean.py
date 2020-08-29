# clean audio extraction

filepath = "/home/aalien/audio/"

from pydub import AudioSegment
import io
import os
import wave
import time

def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':    
        sound = AudioSegment.from_mp3(audio_file_name)  
        audio_file_name = audio_file_name.split('.')[0] + '_.wav'
        sound.export(audio_file_name, format="wav")
      # print("mp3 to wav step:")
      # print(audio_file_name)


def frame_rate_channel(audio_file_name):
    
        with wave.open(audio_file_name, "rb") as wave_file:
            frame_rate = wave_file.getframerate()
            channels = wave_file.getnchannels()
            return frame_rate,channels
            print(frame_rate,channels)
 
def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def audio_convert(audio_file_name):
    
    file_name = filepath + audio_file_name
    mp3_to_wav(file_name)

    # The name of the audio file to transcribe

    frame_rate,channels = frame_rate_channel(file_name)

    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='ru-RU')

if __name__ == "__main__":
    print(frame_rate,channels)
    for audio_file_name in os.listdir(filepath):
        transcript = audio_convert(audio_file_name)