import json

with open('meta-info/BV1P9oYByEy8.json', 'r')  as f:
    meta_data = json.load(f)

with open('meta-info/BV1P9oYByEy8.json', 'w', encoding='utf-8') as f:
    json.dump(meta_data, f, ensure_ascii=False, indent=4)