import json

json_obj = {}
json_obj['dataset_description'] = []
json_obj['dataset_description'].append({'name': 'Example dataset', 'BIDSVersion': '1.0.2'})

with open('/home/mcalvert/week8_analysis/data/dataset_description.json', 'w') as jsonFile:
    json.dump(json_obj, jsonFile)