import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient

load_dotenv(dotenv_path='../.env.search')

# AI Search Endpoints and MGMT key
AI_SEARCH_SERVICE = os.getenv("AI_SEARCH_SERVICE") # search service endpoint https://<your-search-service>.search.windows.net
AI_SEARCH_APIKEY_MGMT = os.getenv("AI_SEARCH_APIKEY_MGMT") # search service admin key   
AI_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION") #"2025-09-01"

# create search index client
index_client = SearchIndexClient(
        endpoint=AI_SEARCH_SERVICE, 
        credential=AzureKeyCredential(AI_SEARCH_APIKEY_MGMT),
        api_version=AI_SEARCH_API_VERSION
        )

###################################################
# LIST INDEXES
###################################################

def list_indexes():
    """ List all Azure AI Search indexes in the existing Resource """
    
    indexes = index_client.list_indexes()
    for index in indexes:
        print("Index name: %s" % index.name)


def get_index_stats(index_name):
    """ Get index stats for a given index """

    # Get index statistics
    try:
        stats = index_client.get_index_statistics(index_name)

        print(f"Index Statistics for '{index_name}':")
        print(f"\tNumber of documents: {stats['document_count']}")
        print(f"\tStorage consumed by index: {stats['storage_size']} bytes")
        print(f"\tStorage consumed by vectors: {stats['vector_index_size']} bytes")
    except Exception as e:
        print(f"Error retrieving statistics for index '{index_name}': {e}")


###################################################
# DELETE INDEX
###################################################

def delete_index(index_name):
    """ Delete Azure AI Search index in the existing Resource """
  
    index_client.delete_index(index_name)
    print("Index %s deleted." %index_name)

###################################################
# DELETE DOCUMENT FROM INDEX
###################################################

def delete_documents_from_index(index_name, documents_to_delete):
    """ Delete document from Azure AI Search index using SDK. Multiple documents can be deleted in a single call.
        Args:
        documents_to_delete: list of documents to delete, each document is a dict with key-value pairs
    """

    search_client = SearchClient(
                        endpoint=AI_SEARCH_SERVICE,
                        index_name=index_name,
                        credential=AzureKeyCredential(AI_SEARCH_APIKEY_MGMT))

    try: 
        # documents_to_delete = [{doc_key_name: doc_key_value}, {...}, ...]
        result = search_client.delete_documents(documents=documents_to_delete)
        for doc in documents_to_delete:
            print(f"Document with key '{doc}' deleted from index '{index_name}'.")

    except Exception as e:
        print(f"Error deleting document '{documents_to_delete}' from index '{index_name}': {e}")





if __name__ == "__main__":
    # list indexes
    list_indexes()

    # get index stats 
    index_name = 'your-test-index-name'  # replace with your index name
    get_index_stats(index_name)

    # delete index
    # delete_index(index_name)
    # list_indexes()

    # delete document from index - test
    # index_name = 'your-index-name_v01'  # replace with your index name
    # get_index_stats(index_name)

    # document_key_name = "chunk_id" # replace with your document key field name
    # document_key_value = 'document_1_0'  # replace with your document key value
    # doc = {document_key_name: document_key_value}
    # docs_to_delete = [doc]
    # delete_documents_from_index(index_name, docs_to_delete)

    get_index_stats(index_name)