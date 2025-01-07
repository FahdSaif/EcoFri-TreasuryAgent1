#fahd: Limit exceeded - NEED to move to hugging face
import openai

# Set your OpenAI API key - No point reusing this- below is garbled or expired. Its just kept as a reference for you to identify it
openai.api_key = "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"

# Test ChatCompletion API
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-instruct",
        messages=[
            {"role": "system", "content": "You are an intelligent assistant."},
            {"role": "user", "content": "Provide a simple test response."}
        ]
    )
    print("OpenAI Response:")
    print(response.choices[0].message['content'].strip())
except openai.error.OpenAIError as e:
    print(f"Error querying OpenAI: {e}")
