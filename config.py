import configparser
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        self.config.read(config_file)
        self.validate_config()

    def validate_config(self):
        required_sections = ['Paths', 'Synthesis', 'AudioEffects', 'AudioProperties', 'VocalizationLabels', 'Output', 'Logging', 'Performance']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required section '{section}' in config file")

        # Validate Paths
        for key in ['input_wav_dir', 'input_textgrid_dir', 'output_wav_dir', 'output_textgrid_dir', 'log_dir']:
            self._validate_path(key)

        # Validate Synthesis parameters
        self._validate_int('Synthesis', 'num_synthetic_files', min_value=1)
        self._validate_float('Synthesis', 'file_length_seconds', min_value=0)
        self._validate_float('Synthesis', 'min_overlap_percentage', min_value=0, max_value=100)
        self._validate_int('Synthesis', 'max_overlaps', min_value=1)
        self._validate_int('Synthesis', 'random_seed')
        self._validate_float('Synthesis', 'amplitude_scaling', min_value=0, max_value=1)
        self._validate_bool('Synthesis', 'normalize_output')
        self._validate_int('Synthesis', 'silence_duration_ms', min_value=0)

        # Validate AudioEffects parameters
        self._validate_bool('AudioEffects', 'apply_effects')
        self._validate_bool('AudioEffects', 'pitch_shift')
        self._validate_float('AudioEffects', 'pitch_shift_semitones')
        self._validate_bool('AudioEffects', 'time_stretch')
        self._validate_float('AudioEffects', 'time_stretch_factor', min_value=0)
        self._validate_bool('AudioEffects', 'amplitude_modulation')
        self._validate_float('AudioEffects', 'amplitude_modulation_frequency', min_value=0)
        self._validate_float('AudioEffects', 'amplitude_modulation_depth', min_value=0, max_value=1)

        # Validate AudioProperties
        self._validate_int('AudioProperties', 'sample_rate', min_value=1)
        self._validate_int('AudioProperties', 'min_segment_length_ms', min_value=1)
        self._validate_int('AudioProperties', 'max_segment_length_ms', min_value=1)

        # Validate VocalizationLabels
        for label, prob in self.config['VocalizationLabels'].items():
            try:
                float_prob = float(prob)
                if not 0 <= float_prob <= 1:
                    raise ValueError(f"Probability for label '{label}' must be between 0 and 1")
            except ValueError:
                raise ValueError(f"Invalid probability value for label '{label}': {prob}")

        # Validate Output
        self._validate_string('Output', 'file_prefix')

        # Validate Logging
        self._validate_int('Logging', 'verbosity_level', min_value=0, max_value=2)

        # Validate Performance
        self._validate_int('Performance', 'thread_count', min_value=1)

    def _validate_path(self, key):
        path = self.config['Paths'][key]
        if not os.path.exists(path):
            raise ValueError(f"Path '{path}' specified for '{key}' does not exist")

    def _validate_int(self, section, key, min_value=None, max_value=None):
        try:
            value = self.config[section].getint(key)
            if min_value is not None and value < min_value:
                raise ValueError(f"'{key}' in section '{section}' must be at least {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"'{key}' in section '{section}' must be at most {max_value}")
        except ValueError:
            raise ValueError(f"Invalid integer value for '{key}' in section '{section}'")

    def _validate_float(self, section, key, min_value=None, max_value=None):
        try:
            value = self.config[section].getfloat(key)
            if min_value is not None and value < min_value:
                raise ValueError(f"'{key}' in section '{section}' must be at least {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"'{key}' in section '{section}' must be at most {max_value}")
        except ValueError:
            raise ValueError(f"Invalid float value for '{key}' in section '{section}'")

    def _validate_bool(self, section, key):
        try:
            self.config[section].getboolean(key)
        except ValueError:
            raise ValueError(f"Invalid boolean value for '{key}' in section '{section}'")

    def _validate_string(self, section, key):
        if not self.config[section][key]:
            raise ValueError(f"'{key}' in section '{section}' cannot be empty")

    def get(self, section, key):
        return self.config[section][key]

    def get_int(self, section, key):
        return self.config[section].getint(key)

    def get_float(self, section, key):
        return self.config[section].getfloat(key)

    def get_bool(self, section, key):
        return self.config[section].getboolean(key)

    def get_vocalization_labels(self):
        labels = {label.lower(): float(prob) for label, prob in self.config['VocalizationLabels'].items()}
        print(f"Loaded vocalization labels: {labels}")  # Temporary print statement for debugging
        return labels

    def get_audio_effects(self):
        effects = {}
        if self.get_bool('AudioEffects', 'apply_effects'):
            if self.get_bool('AudioEffects', 'pitch_shift'):
                effects['pitch_shift'] = self.get_float('AudioEffects', 'pitch_shift_semitones')
            if self.get_bool('AudioEffects', 'time_stretch'):
                effects['time_stretch'] = self.get_float('AudioEffects', 'time_stretch_factor')
            if self.get_bool('AudioEffects', 'amplitude_modulation'):
                effects['amplitude_modulation'] = {
                    'frequency': self.get_float('AudioEffects', 'amplitude_modulation_frequency'),
                    'depth': self.get_float('AudioEffects', 'amplitude_modulation_depth')
                }
        return effects