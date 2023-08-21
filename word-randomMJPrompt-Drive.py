import requests
import streamlit as st
import random
import openai
from midjourney_api import TNL
import concurrent.futures
from bs4 import BeautifulSoup
import time
import databutton as db
from io import BytesIO
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import json
import logging
import streamlit as st

# Set up API keys
openai.api_key = 
TNL_API_KEY = 
tnl = TNL(TNL_API_KEY)

logging.basicConfig(level=logging.INFO)

def authenticate_google_drive(credentials_file):
    """Authenticate with Google Drive using service account credentials file and return the service object."""
    creds = ServiceAccountCredentials.from_service_account_file(credentials_file)
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_drive(service, image_url):
    """Uploads the image from the given URL to Google Drive and returns its link."""
    
    # Get image from URL
    image = Image.open(requests.get(image_url, stream=True).raw)

    # Save image to a file
    image_buffer = BytesIO()
    image.save(image_buffer, format="jpeg")
    image_buffer.seek(0)
    filepath = "temp_image.jpg"
    with open(filepath, 'wb') as f:
        f.write(image_buffer.read())

    # Define metadata for Google Drive
    folder_id =   # The ID of your shared folder
    file_metadata = {
        'name': 'temp_image.jpg',
        'mimeType': 'image/jpeg',
        'parents': [folder_id]
    }

    # Upload the image to Google Drive
    media = MediaFileUpload(filepath, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()

    # Return the link to the uploaded image on Google Drive
    return file['webViewLink']

# Utility Functions for scraping
def fetch_data_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content

def fetch_random_word_from_site():
    url = "https://randomword.com/"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    word_element = soup.find("div", id="random_word")

    if word_element:
        return word_element.text
    return None
   
# Global lists for data
types_of_art_data = []
art_styles_data = []
camera_lenses_data = []
famous_artists_data = []
photographers_data = []

def extract_data(html_content):
    global types_of_art_data, art_styles_data, camera_lenses_data, famous_artists_data, photographers_data
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract "Types of Art"
    types_of_art_data = []
    types_of_art_section = soup.find_all('ol')[0]
    for item in types_of_art_section.find_all('li', recursive=False):
        title = item.find('strong').text
        descriptions = [desc.strip('“”') for desc in item.find('ul').li.text.split(',')]
        types_of_art_data.append((title, descriptions))

    # Extract "Art Styles & Photography"
    art_styles_data = []
    art_styles_section = soup.find_all('ol')[1]
    for item in art_styles_section.find_all('li', recursive=False):
        title = item.find('strong').text
        descriptions = [desc.strip('“”') for desc in item.find('ul').li.text.split(',')]
        art_styles_data.append((title, descriptions))

    # Extract "Camera lenses and filters"
    camera_lenses_data = []
    camera_lenses_section = soup.find_all('ol')[2]
    for item in camera_lenses_section.find_all('li', recursive=False):
        title = item.contents[0].strip(':\n')
        descriptions = [desc.strip('“”') for desc in item.find('ul').li.text.split(',')]
        camera_lenses_data.append((title, descriptions))

    # Extract "45 Famous Artists"
    famous_artists_data = []
    famous_artists_section = soup.find_all('ol')[3]
    for item in famous_artists_section.find_all('li'):
        artist, art_style = item.text.split('–')
        famous_artists_data.append((artist.strip(), art_style.strip()))

    # Extract "25 Photographers"
    photographers_data = []
    photographers_section = soup.find_all('ol')[4]
    for item in photographers_section.find_all('li'):
        name, photo_type = item.text.split('–')
        photographers_data.append((name.strip(), photo_type.strip().replace(' Photography', '')))

    return types_of_art_data, art_styles_data, camera_lenses_data, famous_artists_data, photographers_data

# Utility Functions for MidJourney

def find_key_in_dict(d, target_key):
    """Searches recursively in a dictionary for a target key."""
    for key, value in d.items():
        if key == target_key:
            return value
        elif isinstance(value, dict):
            result = find_key_in_dict(value, target_key)
            if result is not None:
                return result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = find_key_in_dict(item, target_key)
                    if result is not None:
                        return result
    return None

# New Upscale Function
def upscale_image(tnl, button_message_id):
    """Upscale one of the images using a randomly chosen upscale button (U1 to U4)"""
    upscale_button = f"U{random.randint(1, 4)}"
    button_response = tnl.button(upscale_button, button_message_id)
    
    if not button_response or not button_response.get('messageId'):
        st.error(f"Upscale request failed for {upscale_button}")
        return None
    
    new_message_id = button_response['messageId']
    
    # Use check_progress to ensure the upscaled image is generated
    upscaled_image_url, timeout_reached = check_progress(tnl, new_message_id)
    
    if not upscaled_image_url:
        if timeout_reached:
            st.error('Upscaled image generation timed out.')
        else:
            st.error(f"Failed to retrieve upscaled image for {upscale_button}")
        return None
    
    return upscaled_image_url


def get_progress(response):
    """Extracts the progress value from a MidJourney response."""
    if 'progress' in response:
        return response['progress']
    else:
        return None

def extract_full_context(content, snippet):
    """Extracts the full context around a snippet from the content."""
    start_idx = content.find(snippet)
    end_idx = start_idx + len(snippet)
    start_sentence = content.rfind('.', 0, start_idx) + 1
    if start_sentence == 0:  # If the snippet starts at the beginning, don't go back
        start_sentence = start_idx
    end_sentence = content.find('.', end_idx)
    if end_sentence == -1:  # If no more full stops, go to the end
        end_sentence = len(content)
    else:
        end_sentence += 1
    return content[start_sentence:end_sentence].strip()

def get_contextual_summary(snippet, content):
    """Generates a summary of a snippet given its context."""
    full_context = extract_full_context(content, snippet)
    prompt = (f"From the following: {snippet}\n"
              f"in the context of: {full_context}\n"
              f"extract the most newsworthy angle and give a short one sentence summary")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    summary = response.choices[0].message['content'].strip()
    return summary

def get_image_prompt(summary):
    """Generates an image prompt based on a given summary."""
    prompt = f"If you were to convey the essence of this segment through a single powerful visual, what would it be? Think colors, shapes, and forms. Segment: {summary}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

def check_progress(tnl, message_id, max_wait_mins=8):
    """Checks the progress of an image generation request to MidJourney."""
    start_time = time.time()
    while True:
        current_time = time.time() 
        elapsed_mins = (current_time - start_time) / 60
        if elapsed_mins >= max_wait_mins:
            return False, True
        response = tnl.get_message_and_progress(message_id, expire_mins=5)
        progress = get_progress(response)
        image_url = find_key_in_dict(response, 'imageUrl')
        if image_url:
            return image_url, False
        time.sleep(30)
    return None, True

def generate_prompt(topic):
    # Randomly select elements from each list
    art_style_title, art_style_desc = random.choice(art_styles_data)
    type_of_art_title, type_of_art_desc = random.choice(types_of_art_data)
    camera_lens_title, camera_lens_desc = random.choice(camera_lenses_data)
    
    # Combine artists and photographers
    combined_list = famous_artists_data + photographers_data
    artist_or_photographer, style = random.choice(combined_list)
    
    # Construct the prompt
    prompt = (f"{topic}, {random.choice(art_style_desc)}, {random.choice(type_of_art_desc)}, "
              f"{random.choice(camera_lens_desc)}, in the style of {artist_or_photographer}, {style}")
    
    return prompt


# Modified Midjourney Integration Function for Multithreading
def process_prompt(prompt):
    response = tnl.imagine(prompt)
    if 'messageId' in response:
        message_id = response['messageId']
        image_url, timeout_reached = check_progress(tnl, message_id)
        
        if not image_url:
            if timeout_reached:
                st.error('Image generation timed out.')
            else:
                st.error('Image generation failed.')
        else:
            message_response = tnl.get_message_and_progress(message_id, expire_mins=5)
            if message_response.get('progress') == 100:
                button_message_id = find_key_in_dict(message_response, 'buttonMessageId')
                if button_message_id:
                    upscaled_image_url = upscale_image(tnl, button_message_id)
                    return image_url, upscaled_image_url
                else:
                    st.error("Failed to get buttonMessageId for upscaling.")
                    return image_url, None
            else:
                return image_url, None
    return None, None

def app():
    st.title("MidJourney Prompt Generator")

    # Fetch the random word
    random_word = fetch_random_word_from_site()

    # Display the fetched word
    if random_word:
        st.write(f"Random Word: {random_word}")
    else:
        st.error("Failed to fetch the random word.")
        return

    # Extract data from the website
    URL = "https://www.creativindie.com/best-midjourney-prompts-an-epic-list-of-crazy-text-to-image-ideas/"
    html_content = fetch_data_from_url(URL)
    types_of_art_data, art_styles_data, camera_lenses_data, famous_artists_data, photographers_data = extract_data(html_content)

    # Generate the prompts
    prompts = [generate_prompt(random_word) for _ in range(1)]

    st.subheader("Generated Prompt:")
    st.write(prompts[0])

    # Generate the image for the prompt using multithreading
    image_url, upscaled_image_url = process_prompt(prompts[0])

    if image_url:
        st.subheader("Generated Image:")
        st.image(image_url)
    else:
        st.error("Failed to generate image.")

    if upscaled_image_url:
        st.subheader("Upscaled Image:")
        st.image(upscaled_image_url)
    else:
        st.error("Failed to generate upscaled image.")

    # Upload the upscaled image to Google Drive
    try:
        credentials_info = db.storage.json.get(key="credentials-json")
        if not credentials_info:
            st.error("Failed to retrieve credentials from storage.")
            return

        # Ensure that the private key is correctly formatted
        credentials_info['private_key'] = credentials_info['private_key'].replace("\\n", "\n")

        # Authenticate with Google Drive
        creds = ServiceAccountCredentials.from_service_account_info(credentials_info)
        drive_service = build('drive', 'v3', credentials=creds)

        # Upload the image to Google Drive
        image_link_on_drive = upload_to_drive(drive_service, upscaled_image_url)
        st.write(f"Uploaded to Google Drive: [Link]({image_link_on_drive})")

    except Exception as e:
        st.error(f"An error occurred: {e}")
                
if __name__ == "__main__":
    app()





