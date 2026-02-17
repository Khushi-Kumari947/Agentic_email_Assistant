import os
from typing import List, Dict, Any
from pypdf import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            length_function=len
        )
    
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error loading PDF {file_path}: {str(e)}")
    
    def load_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error loading DOCX {file_path}: {str(e)}")
    
    def load_documents(self, directory_path: str) -> List[Dict[str, Any]]:
        """Load all documents from directory"""
        documents = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if filename.endswith('.pdf'):
                text = self.load_pdf(file_path)
                documents.append({
                    "text": text,
                    "metadata": {
                        "source": filename,
                        "type": "pdf",
                        "path": file_path
                    }
                })
            elif filename.endswith('.docx'):
                text = self.load_docx(file_path)
                documents.append({
                    "text": text,
                    "metadata": {
                        "source": filename,
                        "type": "docx",
                        "path": file_path
                    }
                })
        
        return documents
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks"""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc["text"])
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "text": chunk,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                })
        
        return chunked_docs