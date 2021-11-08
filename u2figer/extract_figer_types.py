# extract FIGER types from the figer mappings (with Freebase,
# figer/src/main/resources/edu/washington/cs/figer/analysis/types.map at the FIGER project)

import json

file = open('figer_mapping.txt', 'r')

type_list = []

for line in file:
    _tuple = line.split('\t')
    _type = _tuple[1].lstrip('/').rstrip('\n')
    if _type not in type_list:
        type_list.append(_type)

layer_1_types = []
layer_2_types = []
type_json = []
layerwise_mapping = {}

for item in type_list:
    hierarchy = item.split('/')

    assert len(hierarchy) <= 2

    first = hierarchy[0]
    second = None
    if first not in layer_1_types:
        layer_1_types.append(first)

    if first not in layerwise_mapping:
        layerwise_mapping[first] = []

    if len(hierarchy) == 2:
        second = hierarchy[1]
        if hierarchy[1] not in layer_2_types:
            layer_2_types.append(hierarchy[1])
        if second not in layerwise_mapping[first]:
            layerwise_mapping[first].append(second)

    type_json.append({'name': item, 'first': first, 'second': second})

for item in layer_2_types:
    if item in layer_1_types:
        print(item)

with open('type_list.jsonl', 'w') as fp:
    json.dump(type_list, fp, indent=4)

with open('type_json.jsonl', 'w') as fp:
    json.dump(type_json, fp, indent=4)

with open('type_list_layer1.jsonl', 'w') as fp:
    json.dump(layer_1_types, fp, indent=4)

with open('type_list_layer2.jsonl', 'w') as fp:
    json.dump(layer_2_types, fp, indent=4)

with open('layerwise_type_mapping.jsonl', 'w') as fp:
    json.dump(layerwise_mapping, fp, indent=4)

file.close()