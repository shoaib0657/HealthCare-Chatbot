# PineCone integration for embeddings and retrieval.
from datetime import datetime, time
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
import logging
from config import config
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

class PineconeService:
    def __init__(self):
        """Initialize Pinecone service"""
        self.logger = logging.getLogger(__name__)
        self._initialize_embeddings()
        self._initialize_pinecone()

    def _initialize_embeddings(self) -> None:
        """Initialize embeddings model"""
        try:
            self.embeddings = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
            self.logger.info("Embeddings initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize embeddings: {str(e)}")
            raise

    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client"""
        try:
            self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
            self.index_name = config.PINECONE_INDEX_NAME

            # Check and create index if needed
            if not self.pc.has_index(self.index_name):
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # PubMedBERT dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws', 
                        region='us-east-1'
                    ) 
                )

                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status.ready:
                    time.sleep(1)
            
            self.index = self.pc.Index(self.index_name)
            self.logger.info("Pinecone initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    def index_patient_data(self, patient_id, note: str):
        """Index patient data in Pinecone"""
        try:
            # Generate embedding
            embedding = self.embeddings.encode(note)
            vector_id = uuid.uuid4()

            # Add metadata
            metadata = {
                "note": note,
                "patient_id": str(patient_id),
                "timestamp": datetime.now().isoformat()
            }
            
            # Upsert to Pinecone
            self.insert_vector(patient_id, vector_id, embedding, metadata)
            
            self.logger.info(f"Successfully indexed note for patient {patient_id}")
            return vector_id
        except Exception as e:
            self.logger.error(f"Error indexing patient data: {str(e)}")
            return None

    def insert_vector(self, patient_id, vector_id: uuid.UUID, vector, metadata=None):
        """Insert a vector into patient's namespace"""
        namespace = f"patient_{patient_id}"
        try:
            self.index.upsert(
                vectors=[(str(vector_id), vector, metadata)],
                namespace=namespace
            )
        except Exception as e:
            self.logger.error(f"Error inserting vector: {str(e)}")
            raise

    def delete_vector(self, patient_id, vector_id: uuid.UUID):
        """Delete a vector from patient's namespace"""
        namespace = f"patient_{patient_id}"
        try:
            self.index.delete(
                ids=[str(vector_id)],  # Convert UUID to string
                namespace=namespace
            )
            return True
        except Exception as e:
            self.logger.error(f"Error deleting vector: {str(e)}")
            return False

    def query_vectors(self, patient_id, query_text: str, top_k: int=5):
        """Query similar vectors in patient's namespace"""
        try:
            namespace = f"patient_{patient_id}"
            # Generate embedding for query
            query_vector = self.embeddings.encode(query_text)
            
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True
            )
            return results
        except Exception as e:
            self.logger.error(f"Error querying vectors: {str(e)}")
            raise

    def text_split(self, extracted_data):
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(extracted_data)

        return text_chunks
    
    def load_files(self, data):
        """Load files from data directory"""

        if os.path.isdir(data):

            print("Loading files...")

            loader = DirectoryLoader(
                data,
                glob="*.pdf",
                loader_cls=PyPDFLoader
            )

            documents = loader.load()

            return documents
        else:
            raise ValueError("Invalid data directory")
        
    def download_embedding_model(self):

        model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return model

        
    def upload_documents(self, data):
        """Upload documents to Pinecone"""

        index_name = "medical-books"

        print("Uploading documents...")

        model = self.download_embedding_model()

        print("Model loaded...")

        try:
            if not self.pc.has_index(index_name):

                print("Creating index...")

                self.pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws', 
                        region='us-east-1'
                    ) 
                )

                # Wait for index to be ready
                while not self.pc.describe_index(index_name).status.ready:
                    time.sleep(1)

            index = self.pc.Index(index_name)

            # Load files
            extracted_data = self.load_files(data)

            # Split text into chunks
            text_chunks = self.text_split(extracted_data)

            # Upload documents
            docsearch = PineconeVectorStore.from_documents(
                documents=text_chunks,
                index_name=index_name,
                embedding=model,
                namespace="ns1"
            )

            self.logger.info("Documents uploaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to upload documents: {str(e)}")
            raise