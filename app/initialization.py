from llama_index.core import SummaryIndex, Settings, VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.mistralai import MistralAIEmbedding  # Use MistralAI embeddings
from llama_index.llms.mistralai import MistralAI  # Use MistralAI LLM
from llama_index.core import StorageContext, load_index_from_storage
import nest_asyncio
from dotenv import load_dotenv
import os
import logging
import sys
from llama_index.core.node_parser import SemanticSplitterNodeParser
import json
import markdown2

nest_asyncio.apply()
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
Settings.llm = MistralAI(max_tokens=4000, model="mistral-large-latest", api_key=api_key)
Settings.embed_model = MistralAIEmbedding(
            model_name="mistral-embed", 
            api_key=api_key,
            max_tokens=4000
        )
if not api_key:
    raise ValueError("You must provide an API key to use MistralAI. Set it in the .env file as MISTRAL_API_KEY.")
print("MISTRAL_API_KEY:", api_key)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def initialize_and_persist_vectorstore(dir_path, persist_dir):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    if os.listdir(persist_dir):
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        summary_index = load_index_from_storage(storage_context)
    else:
        reader = SimpleDirectoryReader(input_dir=dir_path)
        documents = reader.load_data()

        Settings.llm = MistralAI(max_tokens=4000, model="mistral-large-latest", api_key=api_key)  # Adapté pour MistralAI
        Settings.embed_model = MistralAIEmbedding(
            model_name="mistral-embed", 
            api_key=api_key,
            max_tokens=4000
        )
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95,embed_model=Settings.embed_model
        )
        nodes = splitter.get_nodes_from_documents(documents)
        summary_index = VectorStoreIndex(nodes,embed_model=Settings.embed_model)
        # summary_index = SummaryIndex.from_documents(documents=documents)
        summary_index.storage_context.persist(persist_dir=persist_dir)
        
    Settings.llm = MistralAI(max_tokens=4000, model="mistral-large-latest", api_key=api_key)
    Settings.embed_model = MistralAIEmbedding(
                model_name="mistral-embed", 
                api_key=api_key,
                max_tokens=4000
            )
    chat_engine = summary_index.as_chat_engine(chat_mode="context",llm=Settings.llm)
    return chat_engine


# def persist_Index(persist_dir):
#     storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
#     summary_index = load_index_from_storage(storage_context)
#     Settings.llm = MistralAI(max_tokens=4000, model="mistral-large-latest", api_key=api_key)
#     Settings.embed_model = MistralAIEmbedding(
#                 model_name="mistral-embed", 
#                 api_key=api_key,
#                 max_tokens=4000
#             )
#     chat_engine = summary_index.as_chat_engine(chat_mode="context",llm=Settings.llm)
#     return chat_engine



def generation_questions(context,chat_engine):
    questions = chat_engine.generate_questions(context)
    return questions

def evaluate_answers_with_chat_engine(chat_engine, answers):
    prompt = f"En s'adressant directement au candidat,Évalue ces réponses suivantes :\n{json.dumps(answers, indent=4, ensure_ascii=False)} et propose un plan de formation basé sur les éléments non maîtrisés, en s'appuyant sur le contexte"
    response = chat_engine.chat(prompt)

    # Debugging statement to print the response
    print("Chat engine response:", response.response)

    if response.response.strip() == "":
        raise ValueError("The chat engine returned an empty response.")

    # Convert the response to Markdown
    markdown_response = markdown2.markdown(response.response)
    return markdown_response