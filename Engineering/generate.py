import os
import re
import yaml
import requests

# 获取 Dropbox 访问令牌
ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    print('Error: DROPBOX_ACCESS_TOKEN is not set.')
    exit(1)

dbx = dropbox.Dropbox(ACCESS_TOKEN)

# 创建 /data 目录
if not os.path.exists('data'):
    os.makedirs('data')

modules = []  # 使用列表来存储模块信息

with open('module.list', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    try:
        # 下载文件内容
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        # 提取 name
        match = re.search(r'(?<=#!name=).*', content)
        if match:
            name = match.group(0)
            original_name = name  # 保存原始的 name

            # 处理 name 以符合 Dropbox 要求
            # 移除特殊字符
            invalid_chars = r'[\/\\<>:"|?*\.\s]+$'
            name = re.sub(invalid_chars, '', name)

            # 移除表情符号和颜文字
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # 表情符号
                                       u"\U0001F300-\U0001F5FF"  # 符号和象形文字
                                       u"\U0001F680-\U0001F6FF"  # 交通和地图符号
                                       u"\U0001F1E0-\U0001F1FF"  # 旗帜
                                       "]+", flags=re.UNICODE)
            name = emoji_pattern.sub(r'', name)

            # 移除因删除表情符号而产生的多余空格
            name = ' '.join(name.split())

            # 截断长度超过 260 的名字
            if len(name) > 260:
                name = name[:260]

            # 去除末尾空格
            name = name.rstrip()

            # 确保 name 不为空
            if not name:
                print(f'Error: Processed name is empty for URL {url}. Skipping.')
                continue

            # 保存 name 和 URL 到 modules 列表
            modules.append({'name': name, 'url': url})

            # 保存文件到 /data 目录
            file_path = os.path.join('data', name)
            with open(file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(content)

            print(f'Successfully processed file: {name}')

            # 上传文件到 Dropbox
            dropbox_path = '/' + os.path.relpath(file_path, start='.')
            with open(file_path, 'rb') as f_upload:
                data = f_upload.read()
                try:
                    dbx.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                    print(f'Successfully uploaded {file_path} to Dropbox path {dropbox_path}.')
                except Exception as e:
                    print(f'Error uploading {file_path}: {e}. Skipping.')
                    continue
        else:
            print(f'Could not extract name from {url}. Skipping.')
            continue
    except Exception as e:
        print(f'Error processing {url}: {e}. Skipping.')
        continue

# 将 modules 列表保存为 modules.yaml
with open('modules.yaml', 'w', encoding='utf-8') as yaml_file:
    yaml.dump(modules, yaml_file, allow_unicode=True)

print('All files processed.')
