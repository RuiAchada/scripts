import subprocess
import logging
import json
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_video.log"),
        logging.StreamHandler()
    ]
)

def load_settings_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
            return settings
    except Exception as e:
        logging.error(f"Failed to load settings from file: {e}")
        return {}

def download_hls_stream(manifest_url, headers, output_filename):
    # Construct the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-headers', '\r\n'.join([f'{key}: {value}' for key, value in headers.items()]),
        '-i', manifest_url,
        '-c', 'copy',
        output_filename
    ]
    
    # Execute the command
    try:
        logging.info(f"Starting download from {manifest_url}")
        subprocess.run(ffmpeg_command, check=True)
        logging.info(f"Video downloaded successfully and saved as {output_filename}")
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred while downloading the video: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Load settings from the settings.json file
    settings = load_settings_from_file('settings.json')

    # Check for a local manifest file path in the settings
    manifest_url = settings.get('manifest_url', None)
    if not manifest_url:
        manifest_url = input("Enter the manifest URL (e.g., .m3u8 file URL): ")

    # Check for an output filename in the settings
    output_filename = settings.get('output_filename', None)
    if not output_filename:
        # Generate the output filename with the current timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_filename = input(f"Enter the output filename (default: video_{timestamp}.mp4): ")
        if not output_filename:
            output_filename = f"video_{timestamp}.mp4"

    # Load headers from the settings file
    headers = settings.get('headers', {})
    if not headers:
        logging.error("No headers found. Please check the settings file.")
    elif not manifest_url:
        logging.error("The manifest URL cannot be empty.")
    elif not output_filename:
        logging.error("The output filename cannot be empty.")
    else:
        download_hls_stream(manifest_url, headers, output_filename)
