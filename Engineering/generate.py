import re
import yaml
import os

with open('modules.list', 'r') as file:
    lines = file.readlines()
data = []
name_pattern = re.compile(r'(?<=#!name=)([^\s]+)')
invalid_chars = r'[/\\<>:"|?*]'
max_path_length = 260
for line in lines:
    url = line.strip() 

    name_match = name_pattern.search(url)
    if name_match:
        name = name_match.group(0)
        cleaned_name = re.sub(invalid_chars, '', name)
        cleaned_name = cleaned_name.rstrip()
        path = os.path.join("output", f"{cleaned_name}.yaml")
        if len(path) > max_path_length:
            print(f"Warning: Path '{path}' exceeds the {max_path_length} character limit and may not save correctly to Dropbox.")
        entry = {'name': cleaned_name, 'url': url}
        data.append(entry)
        print(f"Processed '{name}' -> '{cleaned_name}'")

with open('modules.yaml', 'w') as yaml_file:
    yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)

print("YAML file generated: modules.yaml")
