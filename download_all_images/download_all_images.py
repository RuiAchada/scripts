"""
This script downloads all images from a specified URL. The user provides the URL, and the script retrieves all 
image links (ending in .png, .jpg, .jpeg, or .gif) from the website. It then saves the images into a directory 
named 'images' on the local machine.
"""

import os
import requests
from bs4 import BeautifulSoup

# Get the URL from user input
url = input("Enter the URL of the website: ")

# Make a request to the website
r = requests.get(url)
r.raise_for_status()

# Parse the HTML from the website
soup = BeautifulSoup(r.text, 'html.parser')

# Create a directory for the images
os.makedirs('images', exist_ok=True)

# Loop over all anchor tags
for link in soup.find_all('a'):

    # Get the href attribute
    href = link.get('href')

    # Skip if href is not set or does not end with an image extension
    if href is None or not (href.endswith('.png') or href.endswith('.jpg') or href.endswith('.jpeg') or href.endswith('.gif')):
        continue

    # If the href does not start with 'http', then it is a relative URL, and we should add the base URL to it.
    if not href.startswith('http'):
        href = url.rstrip('/') + '/' + href.lstrip('/')

    # Use the requests library to get the image content
    image_content = requests.get(href).content

    # Get the image name
    image_name = os.path.join('images', href.split('/')[-1])

    # Write the image content to a file
    with open(image_name, 'wb') as f:
        f.write(image_content)

print('Done')
