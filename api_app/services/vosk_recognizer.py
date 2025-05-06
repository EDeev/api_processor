import os, wave, vosk, ffmpeg

MODEL_PATH = r"models/vosk-model-small-ru-0.22"
FFMPEG_PATH = r"models/ffmpeg/bin/ffmpeg.exe"

def convert_audio_to_wav(input_file, output_file, FFMPEG_PATH):
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, format='wav', acodec='pcm_s16le', ar='16000', ac=1,
                    af='acompressor,afftdn,dynaudnorm,aresample=16000')  # 16kHz для Vosk
            .global_args('-loglevel', 'quiet')
            .run(cmd=FFMPEG_PATH, overwrite_output=True)
        )
        print(f"Конвертация завершена: {output_file}")
    except ffmpeg.Error as e:
        print("Ошибка при конвертации:", e.stderr.decode())


vosk.SetLogLevel(-1)

def recognize_speech(audio_path) -> str:
    if not os.path.exists(MODEL_PATH):
        print("Ошибка: Модель не найдена!")
        return ""

    model = vosk.Model(MODEL_PATH)

    if audio_path.split('.')[-1] != "wav":
        convert.convert_audio_to_wav(audio_path, "audio.wav", FFMPEG_PATH)
        audio_path = "audio.wav"
    else:
        with wave.open(audio_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                convert.convert_audio_to_wav(audio_path, "audio.wav", FFMPEG_PATH)
                audio_path = "audio.wav"


    with wave.open(audio_path, "rb") as wf: # использование vosk
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
        while True:
            data = wf.readframes(3200)
            if not data:
                break
            recognizer.AcceptWaveform(data)

    if audio_path == "audio.wav":
        os.remove(audio_path)

    return recognizer.FinalResult().split(": \"")[-1][:-3]
