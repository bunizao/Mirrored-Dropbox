import os
import re
import yaml
import requests

# Create /data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

modules = []  # Use a list to store module information

with open('modules.list', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    try:
        # Download file content
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        # Extract name
        match = re.search(r'(?<=#!name=).*', content)
        if match:
            name = match.group(0)
            original_name = name  # Save the original name

            # Process name to comply with file system requirements
            # Remove special characters
            invalid_chars = r'[\/\\<>:"|?*\.\s]+$'
            name = re.sub(invalid_chars, '', name)

            # Remove emojis and emoticons
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # Emoticons
                                       u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
                                       u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
                                       u"\U0001F1E0-\U0001F1FF"  # Flags
                                       "]+", flags=re.UNICODE)
            name = emoji_pattern.sub(r'', name)

            # Remove extra spaces resulting from emoji removal
            name = ' '.join(name.split())

            # Truncate name if it exceeds 260 characters
            if len(name) > 260:
                name = name[:260]

            # Remove trailing spaces
            name = name.rstrip()

            # Ensure name is not empty
            if not name:
                print(f'Error: Processed name is empty for URL {url}. Skipping.')
                continue

            # Save name and URL to modules list
            modules.append({'name': name, 'url': url})

            # Save file to /data directory
            file_path = os.path.join('data', name)
            with open(file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(content)

            print(f'Successfully processed file: {name}')
        else:
            print(f'Could not extract name from {url}. Skipping.')
            continue
    except Exception as e:
        print(f'Error processing {url}: {e}. Skipping.')
        continue

# Save modules list to modules.yaml
with open('modules.yaml', 'w', encoding='utf-8') as yaml_file:
    yaml.dump(modules, yaml_file, allow_unicode=True)

print('All files processed.')
