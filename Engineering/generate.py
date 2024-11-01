import re
import yaml

with open('modules.list', 'r') as file:
    lines = file.readlines()

data = []
name_pattern = re.compile(r'(?<=#!name=)([^\s]+)')

for line in lines:
    url = line.strip() 
    name_match = name_pattern.search(url)
    if name_match:
        name = name_match.group(0)
        entry = {'name': name, 'url': url}
        data.append(entry)
with open('output.yaml', 'w') as yaml_file:
    yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)

print("YAML generated")
