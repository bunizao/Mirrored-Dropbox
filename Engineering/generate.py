import re
import yaml
import os

# 定义文件名
input_file = 'modules.list'
output_file = 'modules.yaml'

# 定义非法字符和路径长度限制
invalid_chars = r'[/\\<>:"|?*]'
max_path_length = 260

# 正则表达式匹配 name
name_pattern = re.compile(r'(?<=#!name=)([^\s]+)')

# 读取 modules.list 文件
with open(input_file, 'r') as file:
    lines = file.readlines()

# 初始化数据字典
data = {}

# 检查是否已经存在 modules.yaml 文件，如果存在则读取其中的内容
if os.path.exists(output_file):
    with open(output_file, 'r') as yaml_file:
        try:
            existing_data = yaml.safe_load(yaml_file) or []
            # 将现有数据转为字典以便快速查找
            data = {entry['url']: entry['name'] for entry in existing_data if 'url' in entry and 'name' in entry}
        except yaml.YAMLError as e:
            print("Error loading existing modules.yaml:", e)

# 初始化新的数据字典
new_data = {}

# 遍历 modules.list 并处理每个 URL
for line in lines:
    url = line.strip()  # 获取每行的 URL
    # 使用正则表达式提取 name
    name_match = name_pattern.search(url)
    if name_match:
        # 获取 name 并清理非法字符
        name = name_match.group(0)
        cleaned_name = re.sub(invalid_chars, '', name).rstrip()
        
        # 检查路径长度限制
        path = os.path.join("output", f"{cleaned_name}.yaml")
        if len(path) > max_path_length:
            print(f"Warning: Path '{path}' exceeds the {max_path_length} character limit and may not save correctly to Dropbox.")
        
        # 如果该 URL 已在现有文件中，保留用户在 modules.yaml 中的 name 修改
        if url in data:
            new_data[url] = data[url]
            print(f"Retained user-modified name for URL '{url}': '{data[url]}'")
        else:
            # 新增条目
            new_data[url] = cleaned_name
            print(f"New entry added for URL '{url}' with name '{cleaned_name}'")

# 检查现有的 data，找出用户删除或替换的 URL
for url in list(data.keys()):
    if url not in new_data:
        print(f"URL '{url}' has been removed or replaced; removing corresponding entry.")
        data.pop(url)

# 合并新数据到 data 中
data.update(new_data)

# 将数据写入 YAML 文件
output_data = [{'name': name, 'url': url} for url, name in data.items()]
with open(output_file, 'w') as yaml_file:
    yaml.dump(output_data, yaml_file, default_flow_style=False, allow_unicode=True)

print("YAML file generated: modules.yaml")
