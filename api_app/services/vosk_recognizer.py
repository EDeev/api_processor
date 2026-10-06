import json
import logging
import os
import tempfile
import threading
import wave

import ffmpeg
import vosk
from django.conf import settings

logger = logging.getLogger(__name__)
vosk.SetLogLevel(-1)

_model = None
_model_lock = threading.Lock()


class RecognitionError(Exception):
    pass


def get_model():
    """Модель Vosk загружается один раз на процесс (раньше — на каждый запрос, это секунды и сотни МБ)"""
    global _model
    with _model_lock:
        if _model is None:
            if not os.path.isdir(settings.VOSK_MODEL_PATH):
                raise RecognitionError(f"Модель Vosk не найдена: {settings.VOSK_MODEL_PATH}")
            _model = vosk.Model(str(settings.VOSK_MODEL_PATH))
    return _model


def convert_audio_to_wav(input_file, output_file):
    """WAV 16 кГц моно для Vosk, с шумоподавлением и нормализацией громкости"""
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, format='wav', acodec='pcm_s16le', ar='16000', ac=1,
                    af='acompressor,afftdn,dynaudnorm,aresample=16000')  # 16kHz для Vosk
            .global_args('-loglevel', 'error')
            .run(cmd=settings.FFMPEG_BINARY, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RecognitionError("Не удалось прочитать аудиофайл") from e


def is_vosk_ready_wav(path) -> bool:
    try:
        with wave.open(path, "rb") as wf:
            return wf.getnchannels() == 1 and wf.getsampwidth() == 2 and wf.getframerate() == 16000
    except (wave.Error, EOFError):
        return False


def recognize_speech(audio_path) -> str:
    model = get_model()

    # временный файл — свой на каждый запрос (раньше общий audio.wav в текущей папке:
    # одновременные запросы перезаписывали друг другу аудио)
    with tempfile.TemporaryDirectory() as tmp:
        if not (audio_path.lower().endswith(".wav") and is_vosk_ready_wav(audio_path)):
            wav_path = os.path.join(tmp, "audio.wav")
            convert_audio_to_wav(audio_path, wav_path)
            audio_path = wav_path

        # Vosk отдаёт текст по фразам: раньше бралось только FinalResult(), и в длинной записи
        # оставалась лишь последняя фраза
        parts = []
        with wave.open(audio_path, "rb") as wf:
            recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if not data:
                    break
                if recognizer.AcceptWaveform(data):
                    parts.append(json.loads(recognizer.Result()).get("text", ""))
        parts.append(json.loads(recognizer.FinalResult()).get("text", ""))

    return " ".join(p for p in parts if p)
