import json
import re


def extract_transcripts_from_log(logfile_path):
    print(logfile_path)
    pattern = re.compile(r'\{.*\:\s*\[.*\]\s*\}')

    transcripts = []

    with open(logfile_path, 'r') as file:
        data = json.load(file)
        for line in data:
            print('Inspecting line:', line.strip())
            matches = pattern.findall(line)
            for match in matches:
                try:
                    json_obj = json.loads(match)
                    if 'transcript' in json_obj:
                        transcripts.append(json_obj['transcript'])
                except json.JSONDecodeError:
                    continue
    return transcripts

#with open("medicalSampleData.csv", newline ='') as csvfile:
transcripts = extract_transcripts_from_log('transcripts.log')
print('transcripts', transcripts)

for transcript in transcripts:
   print(json.dumps(transcript, indent=2))
