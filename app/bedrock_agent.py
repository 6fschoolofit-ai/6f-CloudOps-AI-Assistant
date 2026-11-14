import boto3

BEDROCK_REGION = "ap-south-1"
MODEL_ID = "apac.amazon.nova-lite-v1:0"

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION
)

def ask_nova(question):
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": question}]
            }
        ],
        inferenceConfig={
            "maxTokens": 500,
            "temperature": 0.2
        }
    )

    return response["output"]["message"]["content"][0]["text"]
