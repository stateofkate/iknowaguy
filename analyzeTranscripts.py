from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": "You are an assistant that analyzes call transcripts. These call transcripts involves a seller saying that they have items to sell at a certain price and quantity. Your job is to identify what the price and quantity agreed upon is."},
        {"role": "user", "content": "The output must be in this format:"
        "======="
        "Price: (final agreed upon price)"
        "Quantity: (final agreed upon quantity)"
        "======="},
    ]
)
