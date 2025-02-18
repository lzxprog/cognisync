from pathlib import Path

with open(Path('D:\BaiduSyncdisk\project\cognisync\data_storage\data.json'),'r') as f:
    for line in f:
        print(line)