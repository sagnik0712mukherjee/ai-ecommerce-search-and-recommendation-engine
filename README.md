# AI-ECommerce-Search-And-Recommendation-Engine

An **AI-powered e-commerce search and recommendation engine** built using **Elasticsearch vector search, semantic embeddings, and Streamlit**, designed to deliver **fast, intelligent product discovery**, relevance-driven search, and item-to-item recommendations.

---

## 🚀 Features

### 🛍️ Browse Experience
- **Basic product browsing** from the home page
- Displays a selection of items:
  - **15 items per batch** (3 rows × 5 columns)
- 📦 **Item cards display**:
  - Product image  
  - Product name  
  - Brand  
  - Price  

---

### 🔍 AI-Driven Search
- **Search bar at the top**
- Supports:
  - Free-text **semantic + keyword search**
- Returns **relevance-ranked results** using:
  - Text matching
  - Dense vector similarity
  - Brand & category signals

---

### 🎯 Product Detail Page (PDP) & Recommendations
- **Items are clickable** from search results or browse grid
- Clicking an item opens a **Product Detail Page (PDP)**
- PDP displays:
  - Product image
  - Product name
  - Brand
  - Price
- Bottom section shows:
  - **5 closest alternative items**
  - Generated using **vector similarity search**
  - Recommendations are **cross-catalog and relevance-ranked**

⚙️ Recommendation logic:
- Based on **semantic embeddings**
- Uses **cosine similarity** on product vectors
- Supports:
  - “Similar items”
  - “You may also like”
  - Substitute discovery

---

### 🧠 AI & Relevance
- **SentenceTransformer embeddings** for semantic understanding
- Vector-based similarity search in Elasticsearch
- Hybrid ranking:
  - Text relevance
  - Semantic similarity
  - Brand & catalog signals

---

### ⚙️ Backend Capabilities
- Elasticsearch aggregations for item grouping
- Optimized indexing with:
  - Custom analyzers
  - Vector fields
- Product ID (`pid`) used as **document ID** for consistency

---

## ⚙️ Setup & Installation
- Clone Repo
- Start Elasticsearch (Docker)
```
docker compose up -d
```
- Set Environment Variables
```
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your_password
```
- Install dependencies
```
pip install -r requirements.txt
```
- Create Index & Ingest Data (refer to "src/pipeline - one-time")
- Run Streamlit App
```
streamlit run app/main.py
```

---

## Author

**Sagnik Mukherjee**  
[GitHub Profile](https://github.com/sagnik0712mukherjee)
