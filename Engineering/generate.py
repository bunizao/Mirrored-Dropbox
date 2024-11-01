import os
import re
import yaml
import requests


if not os.path.exists('data'):
    os.makedirs('data')

modules = []  

with open('modules.list', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
}

for url in urls:
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        content = response.text
        match = re.search(r'#!name\s*=\s*(.*)', content)
        if match:
            name = match.group(1)
            original_name = name 

            invalid_chars = r'[\/\\<>:"|?*\.\s]+$'
            name = re.sub(invalid_chars, '', name)


            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # 表情符号
                                       u"\U0001F300-\U0001F5FF"  # 符号和象形文字
                                       u"\U0001F680-\U0001F6FF"  # 交通和地图符号
                                       u"\U0001F1E0-\U0001F1FF"  # 旗帜
                                       "]+", flags=re.UNICODE)
            name = emoji_pattern.sub(r'', name)

            name = ' '.join(name.split())

            if len(name) > 260:
                name = name[:260]

            name = name.rstrip()

            if not name:
                print(f'Error: Processed name is empty for URL {url}. Skipping.')
                continue

            modules.append({'name': name, 'url': url})

            print(f'Successfully processed file: {name}')
        else:
            print(f'Could not extract name from {url}. Skipping.')
            continue
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred while accessing {url}: {http_err}. Skipping.')
        continue
    except Exception as e:
        print(f'Error processing {url}: {e}. Skipping.')
        continue

with open('modules.yaml', 'w', encoding='utf-8') as yaml_file:
    yaml.dump(modules, yaml_file, allow_unicode=True)

print('All files processed.')
