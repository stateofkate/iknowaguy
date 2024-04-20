#start to set up a series of calls and see what actually gets returend
from retell import Retell

client = Retell()
llm = client.llmcreate()
print(llm.llm_id)

# grab llm id


