import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import datetime
TODAY = datetime.date.today()

from pymilvus import MilvusClient, model, Collection,connections
# MILVUS DB SETUP
# Fast setup could be done using Docker, make sure to open the port when launching the instance

# client = MilvusClient(uri="http://localhost:19530")
# embedding_fn = model.DefaultEmbeddingFunction()
client = MilvusClient(uri="http://localhost:19530")
# connections.connect(
#     alias="default",           # optional name for the connection
#     host="localhost",          # your Milvus host
#     port="19530"               # your Milvus port
# )
nltk.download("punkt_tab")

def create_save_node():
    def create_save(state) -> dict:
        trader_plan = state["investment_plan"]
        embedding_fn = model.DefaultEmbeddingFunction()

        index_params = client.prepare_index_params()  

        index_params.add_index(
            field_name="vector", 
            index_type="FLAT", 
            index_name="vector_index", 
            metric_type="L2", 
            params={} 
        )
        # client.drop_collection("demo_collection")
        if not client.has_collection(collection_name="demo_collection"):
                client.create_collection(
                collection_name="demo_collection",
                index_params = index_params,
                dimension=768)

        if not client.has_partition(collection_name="demo_collection", partition_name=str(TODAY)):
            client.create_partition(collection_name="demo_collection", partition_name=str(TODAY))
        docs = []
        detokenizer = TreebankWordDetokenizer()
        tokens = nltk.word_tokenize(trader_plan)
        chunk_size = 150
        overlap = 50
        for i in range(0,len(tokens),chunk_size-overlap):
            if i+chunk_size <= len(tokens):
                chunk = tokens[i:i+chunk_size]
            else:
                chunk = tokens[i:len(tokens)]
            chunk = detokenizer.detokenize(chunk)
            docs.append(chunk)
        vectors = embedding_fn.encode_documents(docs)
        data = [
            {"id": i, "vector": vectors[i], "text": docs[i]}
            for i in range(len(vectors))
        ]
        client.insert(collection_name="demo_collection", data=data)
        
        
        #TO SEARCH (FOR OTHER AGENTS)
        # res = client.search(
        #     collection_name="demo_collection", 
        #     anns_field="vector", 
        #     data=search,  #THE QUERY FOR RAG
        #     limit=3,  # Top K results
        #     search_params={"params": {}},  
        #     output_fields=["text"]
        # )
        return {"end": True}

    return create_save

