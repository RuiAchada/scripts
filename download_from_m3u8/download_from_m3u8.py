import subprocess
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_video.log"),
        logging.StreamHandler()
    ]
)

def load_headers_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
            return settings.get('headers', {})
    except Exception as e:
        logging.error(f"Failed to load headers from settings file: {e}")
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
    manifest_url = input("Enter the manifest URL (e.g., .m3u8 file URL): ")
    output_filename = input("Enter the output filename (e.g., video.mp4): ")

    # Load headers from the settings file
    headers = load_headers_from_file('settings.json')

    if not headers:
        logging.error("No headers found. Please check the settings file.")
    elif not manifest_url:
        logging.error("The manifest URL cannot be empty.")
    elif not output_filename:
        logging.error("The output filename cannot be empty.")
    else:
        download_hls_stream(manifest_url, headers, output_filename)
