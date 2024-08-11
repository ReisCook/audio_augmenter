import os
import sys
from config import ConfigManager
from logger import Logger
from audio_processor import AudioProcessor
from textgrid_handler import TextGridHandler
from synthesis_engine import SynthesisEngine
from utils import ensure_dir, get_files_with_extension, validate_file_pairs

def main():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to config.ini
    config_path = os.path.join(script_dir, 'config.ini')

    # Initialize configuration
    try:
        config_manager = ConfigManager(config_path)
    except FileNotFoundError:
        print(f"Error: config.ini file not found at {config_path}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error in configuration: {e}")
        sys.exit(1)

    # Initialize logger
    log_dir = config_manager.get('Paths', 'log_dir')
    ensure_dir(log_dir)
    logger = Logger(config_manager.get_int('Logging', 'verbosity_level'), log_dir)

    logger.info("Starting vocalization synthesis program")

    # Initialize components
    audio_processor = AudioProcessor(config_manager)
    textgrid_handler = TextGridHandler()
    synthesis_engine = SynthesisEngine(config_manager, logger, audio_processor)

    # Ensure output directories exist
    output_wav_dir = config_manager.get('Paths', 'output_wav_dir')
    output_textgrid_dir = config_manager.get('Paths', 'output_textgrid_dir')
    ensure_dir(output_wav_dir)
    ensure_dir(output_textgrid_dir)

    # Get input files
    input_wav_dir = config_manager.get('Paths', 'input_wav_dir')
    input_textgrid_dir = config_manager.get('Paths', 'input_textgrid_dir')
    wav_files = get_files_with_extension(input_wav_dir, '.wav')
    textgrid_files = get_files_with_extension(input_textgrid_dir, '.TextGrid')

    # Validate input files
    if not validate_file_pairs(wav_files, textgrid_files):
        logger.error("Mismatched input files. Please ensure each WAV file has a corresponding TextGrid file.")
        sys.exit(1)

    # Get the number of synthetic files to create
    num_synthetic_files = config_manager.get_int('Synthesis', 'num_synthetic_files')

    # Log audio effects configuration
    audio_effects = config_manager.get_audio_effects()
    if audio_effects:
        logger.info(f"Audio effects enabled: {', '.join(audio_effects.keys())}")
        for effect, params in audio_effects.items():
            logger.info(f"  {effect}: {params}")
    else:
        logger.info("Audio effects disabled")

    # Process input files and create synthetic files one at a time
    for i in range(num_synthetic_files):
        try:
            # Randomly select an input file
            wav_file = synthesis_engine.select_random_file(wav_files)
            wav_path = os.path.join(input_wav_dir, wav_file)
            textgrid_path = os.path.join(input_textgrid_dir, wav_file.replace('.wav', '.TextGrid'))

            # Read input files
            audio_data, sample_rate = audio_processor.read_wav(wav_path)
            textgrid_data = textgrid_handler.read_textgrid(textgrid_path)

            # Perform synthesis for a single file
            synthetic_audio, synthetic_textgrid = synthesis_engine.synthesize_single(audio_data, textgrid_data, sample_rate)

            # Save output files
            output_prefix = config_manager.get('Output', 'file_prefix')
            output_wav_path = os.path.join(output_wav_dir, f"{output_prefix}{i+1}.wav")
            output_textgrid_path = os.path.join(output_textgrid_dir, f"{output_prefix}{i+1}.TextGrid")

            audio_processor.write_wav(output_wav_path, synthetic_audio, config_manager.get_int('AudioProperties', 'sample_rate'))
            textgrid_handler.write_textgrid(output_textgrid_path, synthetic_textgrid)

            logger.info(f"Created synthetic file {i+1}/{num_synthetic_files}")

        except Exception as e:
            logger.error(f"Error creating synthetic file {i+1}: {e}")

    logger.info("Vocalization synthesis complete")

if __name__ == "__main__":
    main()