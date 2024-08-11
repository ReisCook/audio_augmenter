import numpy as np
import random

class SynthesisEngine:
    def __init__(self, config_manager, logger, audio_processor):
        self.config = config_manager
        self.logger = logger
        self.audio_processor = audio_processor
        self.random = random.Random(self.config.get_int('Synthesis', 'random_seed'))
        self.sample_rate = self.config.get_int('AudioProperties', 'sample_rate')
        self.audio_effects = self.config.get_audio_effects()
        self.logger.debug(f"Initialized SynthesisEngine with vocalization labels: {self.config.get_vocalization_labels()}")

    def select_random_file(self, file_list):
        return self.random.choice(file_list)

    def synthesize_single(self, audio_data, textgrid_data, original_sample_rate):
        try:
            file_length_seconds = self.config.get_float('Synthesis', 'file_length_seconds')
            min_overlap_percentage = self.config.get_float('Synthesis', 'min_overlap_percentage') / 100
            max_overlaps = self.config.get_int('Synthesis', 'max_overlaps')
            amplitude_scaling = self.config.get_float('Synthesis', 'amplitude_scaling')
            normalize_output = self.config.get_bool('Synthesis', 'normalize_output')
            silence_duration_ms = self.config.get_int('Synthesis', 'silence_duration_ms')
            
            vocalization_labels = self.config.get_vocalization_labels()

            # Extract vocalization segments
            segments = self.extract_segments(textgrid_data, vocalization_labels, audio_data, original_sample_rate)

            if not segments:
                self.logger.warning("No valid segments found. Skipping this file.")
                return None, None

            # Determine if the audio is stereo or mono
            is_stereo = len(audio_data.shape) > 1 and audio_data.shape[1] == 2
            
            # Create synthetic audio
            if is_stereo:
                synthetic_audio = np.zeros((int(file_length_seconds * self.sample_rate), 2))
            else:
                synthetic_audio = np.zeros(int(file_length_seconds * self.sample_rate))

            synthetic_intervals = []

            current_position = 0
            while current_position < len(synthetic_audio):
                # Decide number of overlaps for this section
                num_overlaps = self.random.randint(1, max_overlaps)
                
                # Select segments to overlap
                selected_segments = self.select_segments(segments, num_overlaps)
                
                # Calculate overlap region
                overlap_start = current_position
                overlap_end = min(current_position + max(len(seg) for seg, _ in selected_segments), len(synthetic_audio))
                
                # Mix segments
                mixed_audio = self.mix_segments(selected_segments, overlap_end - overlap_start, amplitude_scaling)
                
                # Apply audio effects if enabled
                if self.audio_effects:
                    mixed_audio = self.apply_audio_effects(mixed_audio)
                
                # Add mixed audio to synthetic audio
                if is_stereo:
                    synthetic_audio[overlap_start:overlap_end] += mixed_audio
                else:
                    synthetic_audio[overlap_start:overlap_end] += mixed_audio.reshape(-1)
                
                # Add interval to synthetic TextGrid
                synthetic_intervals.append((overlap_start / self.sample_rate, overlap_end / self.sample_rate, 'OV'))
                
                # Move current position
                current_position = overlap_end + int(silence_duration_ms * self.sample_rate / 1000)

            # Normalize if required
            if normalize_output:
                if is_stereo:
                    synthetic_audio = self.audio_processor.normalize_audio(synthetic_audio)
                else:
                    synthetic_audio = self.audio_processor.normalize_audio(synthetic_audio.reshape(-1))

            # Create synthetic TextGrid
            synthetic_textgrid = self.create_synthetic_textgrid(synthetic_intervals, file_length_seconds)

            return synthetic_audio, synthetic_textgrid

        except Exception as e:
            self.logger.error(f"Error in synthesize_single: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None, None

    def extract_segments(self, textgrid_data, vocalization_labels, audio_data, original_sample_rate):
        segments = []
        try:
            # Get the first (and only) tier
            tier_name = list(textgrid_data.tierDict.keys())[0]
            tier = textgrid_data.tierDict[tier_name]
            
            self.logger.debug(f"Processing tier: {tier_name}")
            self.logger.debug(f"Vocalization labels from config: {vocalization_labels}")
            
            # Convert vocalization_labels keys to lowercase for case-insensitive comparison
            vocalization_labels = {k.lower(): v for k, v in vocalization_labels.items()}
            
            for interval in tier.entryList:
                self.logger.debug(f"Processing interval: {interval.start} - {interval.end}, label: {interval.label}")
                if interval.label.lower() in vocalization_labels:
                    if self.random.random() < vocalization_labels[interval.label.lower()]:
                        start_sample = int(interval.start * original_sample_rate)
                        end_sample = int(interval.end * original_sample_rate)
                        segment_audio = audio_data[start_sample:end_sample]
                        
                        # Resample if necessary
                        if original_sample_rate != self.sample_rate:
                            segment_audio = self.audio_processor.resample(segment_audio, original_sample_rate, self.sample_rate)
                        
                        segments.append((segment_audio, interval.label))
                        self.logger.debug(f"Added segment with label: {interval.label}")
                else:
                    self.logger.warning(f"Unrecognized label '{interval.label}' in TextGrid. Skipping this interval.")
            
            if not segments:
                self.logger.warning("No valid segments found in the TextGrid file.")
            
        except Exception as e:
            self.logger.error(f"Error in extract_segments: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
        return segments

    def select_segments(self, segments, num_overlaps):
        return self.random.sample(segments, min(num_overlaps, len(segments)))

    def mix_segments(self, segments, mix_length, amplitude_scaling):
        # Determine if the audio is stereo or mono
        is_stereo = len(segments[0][0].shape) > 1 and segments[0][0].shape[1] == 2
        
        if is_stereo:
            mixed_audio = np.zeros((mix_length, 2))
        else:
            mixed_audio = np.zeros(mix_length)
        
        for segment_audio, label in segments:
            start = self.random.randint(0, max(0, mix_length - len(segment_audio)))
            end = min(start + len(segment_audio), mix_length)
            
            if is_stereo:
                mixed_audio[start:end] += segment_audio[:end-start] * amplitude_scaling * self.random.uniform(0.8, 1.0)
            else:
                mixed_audio[start:end] += segment_audio[:end-start, np.newaxis] * amplitude_scaling * self.random.uniform(0.8, 1.0)
        
        return mixed_audio

    def create_synthetic_textgrid(self, intervals, duration):
        from praatio import textgrid
        tg = textgrid.Textgrid()
        
        if not intervals:
            # If no intervals, create a single interval covering the entire duration
            intervals = [(0, duration, 'silence')]
        
        # Ensure the intervals cover the entire duration
        if intervals[0][0] > 0:
            intervals.insert(0, (0, intervals[0][0], 'silence'))
        if intervals[-1][1] < duration:
            intervals.append((intervals[-1][1], duration, 'silence'))
        
        tier = textgrid.IntervalTier('vocalizations', intervals)
        tg.addTier(tier)
        return tg

    def apply_audio_effects(self, audio):
        # Implementation of audio effects application
        # This should be customized based on your specific audio effect requirements
        return audio