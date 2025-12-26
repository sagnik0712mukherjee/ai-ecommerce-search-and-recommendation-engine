# AI-ECommerce-Search-And-Recommendation-Engine

An **AI-powered e-commerce search and recommendation engine** built using **Elasticsearch vector search, semantic embeddings, and Streamlit**, designed to deliver **fast, intelligent product discovery** with real-time autocomplete, category browsing, and relevance-driven search experiences.

---

## 🚀 Features

### 🛍️ Browse Experience
- **Category-first browsing UI** (Amazon / Flipkart–style)
- Vertically stacked **categories**
- Each category shows:
  - 5 product cards in a **horizontal scroll**
  - Lazy pagination via horizontal scroll (`>`)
- Clicking a category:
  - Redirects to **category-specific grid view**
  - Displays **15 items per batch** (3 rows × 5 columns)
  - Infinite vertical scroll

---

### 🔍 Intelligent Search
- **Search bar pinned at the top**
- Supports:
  - **Autocomplete suggestions** from Elasticsearch
  - Suggestions include:
    - Product name
    - Category context
    - Thumbnail image
- Two search flows:
  - Selecting an autocomplete suggestion → **direct semantic search**
  - Pressing Enter without selecting → **free-text semantic + keyword search**

---

### 🎯 Context-Aware Search
- **Global search** from home page (cross-catalog)
- **Scoped search** inside a category (category-restricted results)
- Powered by:
  - Keyword matching
  - Dense vector similarity
  - Relevance boosting

---

### 🧠 AI & Relevance
- **SentenceTransformer embeddings** for semantic understanding
- Vector-based similarity search in Elasticsearch
- Hybrid ranking:
  - Text relevance
  - Semantic similarity
  - Category & brand signals

---

### ⚙️ Backend Capabilities
- Elasticsearch aggregations for:
  - Category discovery
  - Item grouping
- Optimized indexing with:
  - Custom analyzers
  - Vector fields
  - Autocomplete fields
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
