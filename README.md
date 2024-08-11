# Vocalization Synthesis Program

This program generates synthetic animal vocalizations by overlapping and manipulating segments from original recordings. It's designed to be flexible and adaptable for various types of animal vocalization studies.

## Setup

1. Clone this repository.
2. Install the required Python libraries:
   ```
   pip install -r requirements.txt
   ```
3. Prepare your input data:
   - Place WAV files in the `input_wav` directory.
   - Place corresponding TextGrid files in the `input_textgrid` directory.
4. Review and modify `config.ini` according to your needs.

## Usage

Run the main script:

```
python main.py
```

The program will generate synthetic vocalizations based on your input files and configuration settings.

## Configuration

Edit `config.ini` to customize the behavior of the program. Key settings include:

### [Synthesis]
- `num_synthetic_files`: Number of synthetic files to generate
- `file_length_seconds`: Length of each synthetic file
- `min_overlap_percentage`: Minimum overlap between vocalizations
- `max_overlaps`: Maximum number of overlapping vocalizations
- `amplitude_scaling`: Scaling factor for overlapped vocalizations
- `normalize_output`: Whether to normalize the output audio
- `silence_duration_ms`: Duration of silence between vocalizations

### [AudioEffects]
- `apply_effects`: Set to `true` to enable audio effects, `false` to disable
- `pitch_shift`: Enable/disable pitch shifting
- `pitch_shift_semitones`: Amount of pitch shift in semitones
- `time_stretch`: Enable/disable time stretching
- `time_stretch_factor`: Factor for time stretching (e.g., 1.1 for 10% longer)
- `amplitude_modulation`: Enable/disable amplitude modulation
- `amplitude_modulation_frequency`: Frequency of amplitude modulation in Hz
- `amplitude_modulation_depth`: Depth of amplitude modulation (0-1)

### [VocalizationLabels]
- Define labels and their inclusion probabilities (e.g., `PV = 1.0`)

See `config.ini` for all available options and their descriptions.

## Output

The program generates:
- Synthetic WAV files in the `output_wav` directory
- Corresponding TextGrid files in the `output_textgrid` directory
- Log files in the `logs` directory

## Audio Effects

You can enable or disable audio effects using the `apply_effects` option in the `[AudioEffects]` section of `config.ini`. When enabled, you can configure the following effects:

1. Pitch Shift: Alters the pitch of vocalizations without changing duration.
2. Time Stretch: Changes the duration of vocalizations without altering pitch.
3. Amplitude Modulation: Applies a periodic change in volume to the vocalizations.

Each effect can be individually enabled or disabled, and its parameters can be fine-tuned.

## Logging

The program creates detailed log files for each run, including information about the synthesis process and any audio effects applied. The verbosity of logging can be adjusted in the configuration file.

## Extending the Program

To adapt this program for different animals or study needs:
1. Modify the `VocalizationLabels` section in `config.ini`.
2. Adjust synthesis parameters in `config.ini` as needed.
3. If necessary, extend the `SynthesisEngine` class in `synthesis_engine.py` to add new audio processing techniques.

## Contributing

Contributions to improve the program are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License

MIT License

## Contact

[reiscook@gmail.com]