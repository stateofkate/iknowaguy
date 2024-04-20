import json

# Path to log file
class parseTranscript:
    def __init__(self, data_entries):
        self.data_entries = data_entries
    def aggregate_transcripts(self):
        combined_transcript = []
        for entry in self.data_entries:
            data_object = json.loads(entry)
            combined_transcript.extend(data_object['transcript'])
        return combined_transcript

    def return_final_transcript(self, combined_transcript):
        agent_responses = set()
        for transcript in combined_transcript:
            for object in transcript:
                if object['role']  == 'agent':
                    agent_responses.add(object['content'])

        final_transcript = agent_responses.join('\n')
        return final_transcript

    def gettranscript(self):
        combined_transcript = self.aggregate_transcripts()
        final_transcript = self.return_final_transcript(combined_transcript)
        return final_transcript
