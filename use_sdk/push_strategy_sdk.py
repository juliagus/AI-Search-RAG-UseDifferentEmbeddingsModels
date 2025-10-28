#  pip install azure-search-documents

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes.models import (
    SimpleField,
    ComplexField,
    SearchField,
    SearchFieldDataType,    
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch, 
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration    
)

import prep_data
import embeddings as emb

load_dotenv(dotenv_path='../.env.search')

# AI Search Endpoints and MGMT key
AI_SEARCH_SERVICE = os.getenv("AI_SEARCH_SERVICE") # search service endpoint https://<your-search-service>.search.windows.net
AI_SEARCH_APIKEY_MGMT = os.getenv("AI_SEARCH_APIKEY_MGMT") # search service admin key   
#AI_SEARCH_APIKEY_QUERY = os.getenv("AI_SEARCH_APIKEY_QUERY") # search service query key
AI_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION") #"2025-09-01"
INDEX_NAME = os.getenv("AI_SEARCH_INDEX_NAME")

# create search client
search_client = SearchClient(endpoint=AI_SEARCH_SERVICE,
                    index_name=INDEX_NAME,
                    credential=AzureKeyCredential(AI_SEARCH_APIKEY_MGMT))


##################################################
# CREATE AI SEARCH INDEX w VECTOR FIELD
##################################################

def create_index():
    """ Create Azure AI Search index in the existing Resource. 
    Index includes a vector field."""

    index_client = SearchIndexClient(
        endpoint=AI_SEARCH_SERVICE, 
        credential=AzureKeyCredential(AI_SEARCH_APIKEY_MGMT),
        api_version=AI_SEARCH_API_VERSION
        )

    # set vector search profile and vect field dimensions
    vector_dimensions = 1536
    vector_search_profile_name = "vector-profile-01"

    # define fields
    fields = [
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True, searchable=True, 
            filterable=True, stored=True, sortable=True, facetable=False),
        SimpleField(name="parent_id", type=SearchFieldDataType.String, searchable=True,   
            filterable=True, stored=True, sortable=True, facetable=False),
        SearchableField(name="document_title", type=SearchFieldDataType.String, searchable=True, 
            filterable=True),
        SearchableField(name="content_text", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="content_embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name=vector_search_profile_name
            )
        ]

    # define vector search profile
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="hnsw-vector-config-1", kind="hnsw"),
            ExhaustiveKnnAlgorithmConfiguration(name="eknn-vector-config", kind="exhaustiveKnn")
        ],
        profiles=[
            VectorSearchProfile(name=vector_search_profile_name, 
                algorithm_configuration_name="hnsw-vector-config-1")
        ]
        )

    # Create the search index with the semantic settings
    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)

    # Create index from schema
    #index_client.create_index(index)
    index_client.create_or_update_index(index)
    print("Index %s created." %INDEX_NAME)

###############################################
# Push data to index
###############################################

def index_push_data(data_path):

    # create documents collection corresponding to search index schema
    search_action = "upload"
    documents = prep_data.process_documents_for_sdk(data_path, search_action)

    # upload documents
    try:
        result = search_client.upload_documents(documents=documents)
        for r in result:
            print(f"Key: {r.key}, Succeeded: {r.succeeded}, ErrorMessage: {r.error_message}")
    except Exception as ex:
        print("Failed to upload documents:", ex)

###############################################
# VECTOR SEARCH
###############################################

def vector_search(query_text):
    """ Perform vector search on the index """
    
    print("\n\n[VECTOR SEARCH] Query: %s, index %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" %(query_text, INDEX_NAME))

    # generate embedding for the query
    query_embedding = emb.create_embedding_simple(query_text)

    try:
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=10,
            fields="content_embedding",
            kind="vector",
            exhaustive=False
        )
        
        results = search_client.search(
            vector_queries=[vector_query],
            select=["document_title, content_text"],
            top=3,
            include_total_count=True
        )

        print(f"Total results: {results.get_count()}")
        for result in results:
            doc = result  # result is a dict-like object
            print('Score: %s' %doc['@search.score'])
            print(doc)
            print('\n')
    except Exception as ex:
        print("Vector search failed:", ex)


def hybrid_search(query_text):
    """ Perform hybrid search on the index """  

    print("\n\n[HYBRID SEARCH] Query: %s, index %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" %(query_text, INDEX_NAME))

    # generate embedding for the query
    query_embedding = emb.create_embedding_simple(query_text)

    try:
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=10,
            fields="content_embedding",
            kind="vector",
            exhaustive=True
        )

        results = search_client.search(
            include_total_count=True,
            search_text=query_text,  # keyword part
            select=["chunk_id", "parent_id", "document_title", "content_text"],
            top=5,
            vector_queries=[vector_query]
        )

        print(f"Total hybrid results: {results.get_count()}")
        for result in results:
            doc = result
            score = result.get("@search.score", "N/A")
            print(f"- Score: {score}")
            print(f"  Chunk ID: {doc['chunk_id']}")            
            print(f"  Parent ID: {doc['parent_id']}")
            print(f"  Doc Title: {doc.get('document_title')}")
            print(f"  Content Text: {doc.get('content_text')}\n")

    except Exception as e:
        print("Hybrid search failed:", e)


if __name__ == "__main__":

    # create index
    create_index()

    # push data to index
    data_path = "../data/"
    index_push_data(data_path)

    # query vector
    query_text = "what is the landmark in Xinjiang?"
    vector_search(query_text)
    hybrid_search(query_text)


