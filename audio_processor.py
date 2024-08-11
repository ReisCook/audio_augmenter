import numpy as np
import soundfile as sf
from scipy import signal
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self, config_manager):
        self.config = config_manager
        self.sample_rate = self.config.get_int('AudioProperties', 'sample_rate')

    def read_wav(self, file_path):
        audio_data, sample_rate = sf.read(file_path)
        if sample_rate != self.sample_rate:
            audio_data = self.resample(audio_data, sample_rate, self.sample_rate)
        return audio_data, self.sample_rate

    def write_wav(self, file_path, audio_data, sample_rate):
        sf.write(file_path, audio_data, sample_rate)

    def resample(self, audio_data, orig_sr, target_sr):
        return signal.resample(audio_data, int(len(audio_data) * target_sr / orig_sr))

    def normalize_audio(self, audio_data):
        return audio_data / np.max(np.abs(audio_data))

    def apply_pitch_shift(self, audio_data, semitones):
        # Convert numpy array to AudioSegment
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=audio_data.dtype.itemsize,
            channels=1
        )
        
        # Apply pitch shift
        shifted = audio_segment.pitch_shift(semitones)
        
        # Convert back to numpy array
        shifted_array = np.array(shifted.get_array_of_samples())
        
        # Ensure the output has the same length as the input
        if len(shifted_array) > len(audio_data):
            shifted_array = shifted_array[:len(audio_data)]
        elif len(shifted_array) < len(audio_data):
            shifted_array = np.pad(shifted_array, (0, len(audio_data) - len(shifted_array)))
        
        return shifted_array

    def apply_time_stretch(self, audio_data, stretch_factor):
        return signal.resample(audio_data, int(len(audio_data) * stretch_factor))

    def apply_amplitude_modulation(self, audio_data, mod_freq, mod_depth):
        t = np.arange(len(audio_data)) / self.sample_rate
        modulation = 1 + mod_depth * np.sin(2 * np.pi * mod_freq * t)
        return (audio_data * modulation).astype(audio_data.dtype)

    def add_background_noise(self, audio_data, snr_db):
        signal_power = np.mean(audio_data ** 2)
        noise_power = signal_power / (10 ** (snr_db / 10))
        noise = np.random.normal(0, np.sqrt(noise_power), len(audio_data))
        return audio_data + noise