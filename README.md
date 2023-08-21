# Midjourney Prompt Generator to Google Drive

This script is designed to utilize the power of The Next Leg API, a community extension of Midjourney. By integrating The Next Leg into your applications, you can leverage the creative capabilities of Midjourney and enhance the user experience of your products.

## Getting Started

[The Next Leg](https://www.thenextleg.io/) is a community extension of Midjourney that provides API access to the platform's features and services. 

### Features

- **Instant Setup**: Begin using the API immediately.
- **Fully Managed**: No need to worry about backend management.
- **Fully Featured**: Includes functionalities like Imagine, Describe, Zoom, Pan, and more.
- **Continuous Updates**: Always stay updated with the latest features.
- **Multi-Account Setup**: Manage multiple accounts seamlessly.
- **Banned Word Prefilter**: Ensure content remains appropriate.
- **Note**: The Next Leg is not an official Midjourney API. It was developed by avid Midjourney users.

## Setup

1. Obtain the necessary API keys from OpenAI and The Next Leg and you will need to setup the Google Drive API and share a folder there with the email address from the credentials.json fil and you will also want that saved.
2. Replace the placeholders in the script (`YOUR_OPENAI_API_KEY` and `YOUR_TNL_API_KEY`) with your actual API keys.
3. Install the necessary Python libraries by running: `pip install -r requirements.txt` or if you are using https://databutton.com/ like me then add them in the settings.  

## Google Drive Integration

This script has the capability to save generated images directly to Google Drive. To set up this functionality, you need to follow the steps mentioned below:

### Enabling the Google Drive API:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project drop-down and select or create the project that you wish to use for accessing Google Drive.
3. Use the navigation menu and navigate to `APIs & Services > Library`.
4. In the library, search for "Drive" and select `Google Drive API`.
5. Click `ENABLE` to turn on the API for your selected project.

### Creating Service Account Credentials:

1. After enabling the API, navigate to `APIs & Services > Credentials`.
2. Click on `+ CREATE CREDENTIALS` and select `Service account`.
3. Fill in the required fields to create the service account.
4. Once the service account is created, click on the service account name.
5. Navigate to the `KEYS` tab and click on `ADD KEY > JSON`.
6. Your browser will download a JSON file containing the credentials. Store this file securely, as it will be used to authenticate your script with Google Drive.

### Setting up the Shared Folder on Google Drive:

1. Create a new folder in your Google Drive where you want the images to be saved.
2. Share this folder with the email address mentioned in the JSON file you downloaded (it will be under the key `client_email`).
3. Once shared, right-click on the folder and select `Get shareable link`. Turn on the sharing link if it's turned off.
4. Copy the last part of the URL (after the last `/`). This is the folder ID.

### Updating the Script:

1. Open the script and replace the placeholder for the `folder_id` with the folder ID you copied in the previous step.
2. Also, ensure that you correctly input the path or content of the JSON file for authentication.

By following the above steps, your script will be able to save generated images directly to your Google Drive.


## Usage

After setting up, run the script. It will fetch a random word, generate a creative prompt based on that word, create an image using The Next Leg's API, and upscale one of the 4 images.  You could adapt it to upscale all of them with a for loop.  

## Need Help?

If you're a beginner programmer or just need some assistance, feel free to ask for help. The community around Midjourney and The Next Leg is always ready to support!

## Credits

This script uses the [The Next Leg API](https://www.thenextleg.io/), developed by the Midjourney community. The Next Leg is not officially associated with Midjourney but is developed by its avid users.

