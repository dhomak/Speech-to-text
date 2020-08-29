# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
filepath = "/home/aalien/audio/"
output_filepath = "/home/aalien/Transcripts/"


# %%
from pydub import AudioSegment
import io
import os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage


# %%
def mp3_to_wav(audio_file_name):
    if audio_file_name.endswith('mp3'):
        sound = AudioSegment.from_mp3(filepath + audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        res = sound.export(filepath + audio_file_name, format="wav")
        res.close()

# %%
def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels


# %%
def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


# %%
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # WARNING: this is a workaround for a google-cloud-storage issue as reported on:
    # https://github.com/googleapis/python-storage/issues/74
    blob._chunk_size = 8388608  # 1024 * 1024 B * 16 = 8 MB

    blob.upload_from_filename(source_file_name)


# %%
def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


# %%
def google_transcribe(audio_file_name):
    
    file_name = filepath + audio_file_name
    mp3_to_wav(file_name)

    # The name of the audio file to transcribe
    
    frame_rate, channels = frame_rate_channel(file_name)
    
    if channels > 1:
        stereo_to_mono(file_name)
    
    bucket_name = 'aalien-bucket-02'
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name
    
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    
    gcs_uri = 'gs://aalien-bucket-02/' + audio_file_name
    transcript = ''
    
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='ru-RU')

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    delete_blob(bucket_name, destination_blob_name)
    return transcript


# %%
def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close() 


# %%
if __name__ == "__main__":
    for audio_file_name in os.listdir(filepath):
        if audio_file_name.endswith('.wav'):
            transcript = google_transcribe(audio_file_name)
            transcript_filename = audio_file_name.split('.')[0] + '.txt'
            write_transcripts(transcript_filename, transcript)
        elif audio_file_name.endswith('.mp3'):
            mp3_to_wav(audio_file_name)

# %%
