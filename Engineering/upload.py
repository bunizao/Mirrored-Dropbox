import os
import yaml
import requests
import dropbox
import re

# Get Dropbox access token
ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    print('Error: DROPBOX_ACCESS_TOKEN is not set.')
    exit(1)

dbx = dropbox.Dropbox(ACCESS_TOKEN)

# Create /data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Custom headers
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
}

# Read modules.yaml
with open('modules.yaml', 'r', encoding='utf-8') as yaml_file:
    modules = yaml.safe_load(yaml_file)

for module in modules:
    name = module.get('name')
    url = module.get('url')
    if not name or not url:
        print(f'Invalid module entry: {module}. Skipping.')
        continue

    try:
        # Download file content without URL replacement
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.text

        # Process name to comply with Dropbox requirements
        # Remove special characters
        invalid_chars = r'[\/\\<>:"|?*\.\s]+$'
        processed_name = re.sub(invalid_chars, '', name)

        # Remove emojis and emoticons
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # Emoticons
                                   u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
                                   u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
                                   u"\U0001F1E0-\U0001F1FF"  # Flags
                                   "]+", flags=re.UNICODE)
        processed_name = emoji_pattern.sub(r'', processed_name)

        # Remove extra spaces
        processed_name = ' '.join(processed_name.split())

        # Truncate name if it exceeds 260 characters
        if len(processed_name) > 260:
            processed_name = processed_name[:260]

        # Remove trailing spaces
        processed_name = processed_name.rstrip()

        # Ensure processed_name is not empty
        if not processed_name:
            print(f'Error: Processed name is empty for URL {url}. Skipping.')
            continue

        # Save file to /data directory
        file_path = os.path.join('data', processed_name)
        with open(file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(content)

        print(f'Successfully downloaded and saved file: {processed_name}')

        # Upload file to Dropbox
        dropbox_path = '/' + os.path.relpath(file_path, start='.')
        with open(file_path, 'rb') as f_upload:
            data = f_upload.read()
            try:
                dbx.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                print(f'Successfully uploaded {file_path} to Dropbox path {dropbox_path}.')
            except Exception as e:
                print(f'Error uploading {file_path}: {e}. Skipping.')
                continue

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred while accessing {url}: {http_err}. Skipping.')
        continue
    except Exception as e:
        print(f'Error processing {url}: {e}. Skipping.')
        continue

print('All files processed and uploaded.')
