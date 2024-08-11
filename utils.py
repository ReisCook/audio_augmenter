import os

def ensure_dir(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_files_with_extension(directory, extension):
    """Get a list of files with a specific extension in a directory."""
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def validate_file_pairs(wav_files, textgrid_files):
    """Validate that each WAV file has a corresponding TextGrid file."""
    wav_basenames = set(os.path.splitext(f)[0] for f in wav_files)
    textgrid_basenames = set(os.path.splitext(f)[0] for f in textgrid_files)
    
    if wav_basenames != textgrid_basenames:
        missing_wav = textgrid_basenames - wav_basenames
        missing_textgrid = wav_basenames - textgrid_basenames
        
        if missing_wav:
            print(f"Warning: Missing WAV files for TextGrids: {', '.join(missing_wav)}")
        if missing_textgrid:
            print(f"Warning: Missing TextGrid files for WAVs: {', '.join(missing_textgrid)}")
        
        return False
    return True