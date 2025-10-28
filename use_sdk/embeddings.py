import os
from dotenv import load_dotenv

############################################
# EMBDEDDING
#############################################
from openai import OpenAI

load_dotenv(dotenv_path='../.env.search')

EMBEDDING_EDP = os.getenv("EMBEDDING_EDP")
EMBEDDING_KEY = os.getenv("EMBEDDING_KEY")
#EMBEDDING_MODEL_NAME = "text-embedding-3-small"
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

def create_embedding_simple(text):
    """ Create embedding using OpenAI SDK """

    print("EMBEDDING: %s, endpoint %s" %(EMBEDDING_MODEL_NAME, EMBEDDING_EDP))

    model = EMBEDDING_MODEL_NAME
    client = OpenAI(
        base_url=EMBEDDING_EDP,
        api_key=EMBEDDING_KEY,
        default_headers= {
                    # "Authorization": "Bearer token",
                          "api-key": EMBEDDING_KEY
                        },
    )

    response = client.embeddings.create(
        input=text,
        model=model
    )
    embedding = response.data[0].embedding
    return embedding