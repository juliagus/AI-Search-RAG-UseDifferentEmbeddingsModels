""" Prepare the data to be pushed to Azure AI Search Index"""

import os
from dotenv import load_dotenv
import embeddings as emb

#############################################
# Prepare the data to PUSH to INDEX
#############################################

def process_documents_for_sdk(folder_path, search_action):
    """ Process documents in a folder to prepare for pushing to Azure AI Search Index using SDK """
    # for simplicity no chunking, docs as is, chunking and all preprocessing to be implemented separately
    # batching should be added as well

    #search_action = "upload"
    # document structure aligned to index definition
    doc = {
        "@search.action": search_action,
        "chunk_id": "",
        "parent_id": "",
        "document_title": "",
        "content_text": "",
        "content_embedding": []       
    }
    documents_collection = []

    for f in os.listdir(folder_path):
        if f.endswith(".txt"):
            print('FILE: %s' %f)
            file_path = os.path.join(folder_path, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # generate embedding for the content
                embedding = emb.create_embedding_simple(content)
                print(f"Processed {f} with embedding: {embedding[:5]}...")

            # create document record and append
            doc_record = doc.copy()
            doc_record["content_text"] = content
            doc_record["content_embedding"] = embedding
            doc_record["chunk_id"] = f.split('.txt')[0] + "_0"
            doc_record["document_title"] = f
            doc_record["parent_id"] = f.split('.txt')[0]
            # add the doc
            documents_collection.append(doc_record)

    #print(documents_collection[0])
    return documents_collection

if __name__ == "__main__":
    data_path = "../data/"
    search_action = "upload"  # or "mergeOrUpload", "delete", etc.
    process_documents_for_sdk(data_path, search_action)