import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_video.log"),
        logging.StreamHandler()
    ]
)

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

    # Headers extracted from the cURL command (these are the headers for a specific website, you may need to change them)
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://vidmoly.to',
        'Referer': 'https://vidmoly.to/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    if not manifest_url:
        logging.error("The manifest URL cannot be empty.")
    elif not output_filename:
        logging.error("The output filename cannot be empty.")
    else:
        download_hls_stream(manifest_url, headers, output_filename)
