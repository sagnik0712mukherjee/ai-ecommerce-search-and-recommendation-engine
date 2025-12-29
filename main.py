import os
import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.browse.browse_categories import get_all_categories
from src.browse.browse_items import get_all_items
from src.recommendations.recommendations import pdp_recommendations
from src.search.search import search_catalog
from src.services.queue_service import start_rerank_worker
from src.ui_helpers.result_grid import render_results_grid
from config import config


# ================= START RERANK WORKER (SAFE) =================
# 🔒 Ensure worker starts ONLY ONCE per Streamlit session
if "rerank_worker_started" not in st.session_state:
    start_rerank_worker()
    st.session_state["rerank_worker_started"] = True
# =============================================================


# ----------------- CACHED BACKEND -----------------
@st.cache_resource(show_spinner="Loading AI model...")
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def get_es_client():
    return Elasticsearch(
        config.ELASTICSEARCH_URL,
        basic_auth=(
            config.ELASTICSEARCH_USER,
            config.ELASTICSEARCH_PASSWORD
        ),
        verify_certs=False
    )

model = load_model()
es = get_es_client()
INDEX_NAME = config.INVENTORY_INDEX


# ----------------- SESSION STATE -----------------
if "view" not in st.session_state:
    st.session_state.view = "HOME"

if "selected_item" not in st.session_state:
    st.session_state.selected_item = None


# ----------------- PAGE CONFIG -----------------
st.set_page_config(layout="wide")


# ----------------- GLOBAL STYLES -----------------
st.markdown("""
<style>
:root {
    --accent-bg: #f3efe7;
    --accent-bg-soft: #faf7f2;
    --accent-border: #d6cfc2;
    --text-black: #000000;
}
.stApp {
    background: linear-gradient(135deg, #6fa8ff, #ff8a8a);
}
* {
    color: var(--text-black) !important;
}
h1, h2, h3, h4, h5 {
    color: var(--text-black) !important;
}
.search-wrapper {
    max-width: 440px;
    margin: 0 auto 24px auto;
}
div[data-baseweb="input"] {
    background: none !important;
    width: 100% !important;
    max-width: 440px !important;
    margin: 0 auto !important;
}
div[data-baseweb="input"] > div {
    border-radius: 12px;
    background-color: var(--accent-bg);
    border: 1px solid var(--accent-border);
    padding: 4px 12px;
}
div[data-baseweb="input"] input {
    font-size: 16px;
    font-weight: 500;
}
button {
    background-color: var(--accent-bg) !important;
    border-radius: 10px !important;
    border: 1px solid var(--accent-border) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ================= PDP VIEW =================
if st.session_state.view == "PDP" and st.session_state.selected_item:

    item = st.session_state.selected_item

    if st.button("⬅ Back"):
        st.session_state.view = "HOME"
        st.session_state.selected_item = None
        st.rerun()

    st.subheader("📌 Product Details")

    st.markdown(
        f"""
        <div class="pdp-container">
            <img src="{item.get('item_image_url', '')}" />
            <div>{item.get('name')}</div>
            <div>{item.get('brand')}</div>
            <div>{item.get('product_id')}</div>
            <div>₹ {item.get('discounted_price')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔁 You may also like")

    recommended_items = pdp_recommendations(
        item_name=item.get("name"),
        item_pid=item.get("product_id"),
        model=model,
        INDEX_NAME=INDEX_NAME,
        es=es,
        num_recs=5
    )

    render_results_grid(recommended_items)
    st.stop()


# ================= HOME VIEW =================
st.title("🛒 Lets Go Shopping!")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    user_query = st.text_input("", placeholder="Search for products...")

if user_query:
    results = search_catalog(
        user_query=user_query,
        _from=0,
        size=20,
        model=model,
        INDEX_NAME=INDEX_NAME,
        es=es
    )
    st.subheader(f"Search Results ({len(results)})")
    render_results_grid(results)

else:
    st.subheader("🛍️ Popular Categories")

    all_categories_with_counts = get_all_categories(es, INDEX_NAME)[:25]

    browse_items = get_all_items(
        es=es,
        INDEX_NAME=INDEX_NAME,
        size=15
    )

    render_results_grid(browse_items)
