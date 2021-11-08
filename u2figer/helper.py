import json

with open('type_list.jsonl', 'r', encoding='utf8') as fp:
    lines = json.load(fp)

lines.sort()
for line in lines:
    print(line)