import os
import sys

import assemblyai as aai
from moviepy.editor import VideoFileClip
from pytube import YouTube

aai.api_key = os.environ['ASSEMBLYAI_API_KEY']
tmpDir = os.environ['TMPDIR']
lockPath = tmpDir + '/lock'
videoPath = tmpDir + '/video.mp4'
audioPath = tmpDir + '/audio.wav'
transcriptDatabasePath = os.environ['TRANSCRIPT_DATABASE_PATH']
videoUrl = sys.argv[1]

if os.path.exists(lockPath):
    print('Existing lock file `' + lockPath + '` found, exiting...')
    exit(1)
    pass

os.makedirs(tmpDir, exist_ok=True)
open(lockPath, 'w').close()

try:
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code="cs", )
    transcriber = aai.Transcriber()

    youtubeObject = YouTube(videoUrl)
    videoId = youtubeObject.video_id
    youtubeObject = youtubeObject.streams.get_highest_resolution()

    print("Downloading video...")

    youtubeObject.download(filename=videoPath)

    print("Downloaded video")
    print("Extracting audio...")

    videoClip = VideoFileClip(videoPath)
    videoClip.audio.write_audiofile(
        audioPath,
        codec="pcm_s16le",
        fps=44100,
        nbytes=4,
        bitrate="16k",
        verbose=False,
        logger=None,
    )

    print("Extracted audio")
    print("Transcribing...")

    transcription = transcriber.transcribe(audioPath, config)

    if transcription.status == aai.TranscriptStatus.error:
        raise Exception("Transcription failed" + transcription.error)

    print("Transcribed")
    print("Exporting transcript...")

    transcript = '\n'.join([paragraph.text for paragraph in transcription.get_paragraphs()])

    transcriptPath = transcriptDatabasePath + '/' + videoId + '.txt'
    open(transcriptPath, 'w').write(transcript)

    print("Exported transcript")
    print("Done")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    os.remove(lockPath)
    pass
