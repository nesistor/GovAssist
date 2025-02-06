# **RAG Service for Web Content Indexing & Retrieval** 🚀  

## **Overview**  
This is a **Retrieval-Augmented Generation (RAG) service** designed to:  
✅ **Crawl and process website content** (from `sitemap.xml`)  
✅ **Chunk text intelligently** while respecting code blocks and paragraphs  
✅ **Generate vector embeddings** using OpenAI's embedding API (`api.x.ai`)  
✅ **Store processed chunks & embeddings** in **Firestore**  
✅ **Provide an API for retrieving relevant content** using semantic search  

---

## **📌 Features**  
- **🔥 Fast & Async**: Uses `FastAPI` for quick content retrieval.  
- **🧠 Smart Chunking**: Splits text at **meaningful points** (sentences, paragraphs, code blocks).  
- **📡 Firestore Storage**: Stores processed web content and embeddings for efficient retrieval.  
- **🎯 Semantic Search**: Retrieves the **most relevant** content based on user queries.  

---

## **📦 Installation**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/nesistor/rag-service.git
cd rag-service
