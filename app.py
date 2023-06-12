import os
import getpass
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import DeepLake
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API Key:')
os.environ['ACTIVELOOP_TOKEN'] = getpass.getpass('Activeloop Token:')
os.environ['ACTIVELOOP_USERNAME'] = getpass.getpass('Activeloop Username:')
username = os.getenv("ACTIVELOOP_USERNAME")
folder_name = input("Insert the folder name: (./foldername example)")

embeddings = OpenAIEmbeddings() # type: ignore


def laod_folder(path):
    docs = []
    for dirpath,dirnames,filenames in os.walk(path):
        for file in filenames:
            try:
                loader = TextLoader(os.path.join(dirpath,file),encoding='utf-8')
                docs.extend(loader.load_and_split())
            except:
                pass
    return docs


def upload_data(texts):
    db = DeepLake(dataset_path=f"hub://{username}/{folder_name}", embedding_function=embeddings)
    db.add_documents(texts)


def get_retriver(db):
    retriver = db.as_retriever()
    retriver.search_kwargs['distance_metric'] = 'cos'
    retriver.search_kwargs['fetch_k'] = 100
    retriver.search_kwargs['maximal_marginal_relevance'] = True
    retriver.search_kwargs['k'] = 10
    return retriver

    
try:
    db = DeepLake(dataset_path=f"hub://{username}/{folder_name}", embedding_function=embeddings)
except:
    docs = laod_folder(folder_name)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    upload_data(texts)
    db = DeepLake(dataset_path=f"hub://{username}/{folder_name}", embedding_function=embeddings)


retriver = get_retriver(db)
model = ChatOpenAI(model='gpt-3.5-turbo') # type: ignore
qa = ConversationalRetrievalChain.from_llm(model,retriever=retriver)

chat_history = []
question = """
Sei uno Sviluppatore con Anni di Esperienza
Il tuo compito è scrivere tutta la documentazione del progetto che stai sviluppando
Dovrai leggere tutto il codice che compone il progetto e scrivere un introduzione alla finalità del progetto seguita poi da una definizione della struttura del codice a cui allegherai lo scopo di quella determinata componente
"""
result = qa({"question": question, "chat_history": chat_history})
chat_history.append(result['answer'])

with open("TEST.md","w") as f:
    f.write(result['answer'])





