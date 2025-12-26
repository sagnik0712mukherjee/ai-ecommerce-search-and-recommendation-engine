import os
import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.browse.browse_categories import get_all_categories
from src.browse.browse_items import get_all_items
from src.recommendations.recommendations import pdp_recommendations
from src.search.search import search_inventory
from src.ui_helpers.result_grid import render_results_grid


# ----------------- CACHED BACKEND -----------------
@st.cache_resource(show_spinner="Loading AI model...")
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def get_es_client():
    return Elasticsearch(
        os.getenv("ELASTICSEARCH_URL"),
        basic_auth=(
            os.getenv("ELASTICSEARCH_USER"),
            os.getenv("ELASTICSEARCH_PASSWORD")
        ),
        verify_certs=False
    )

model = load_model()
es = get_es_client()
INDEX_NAME = "flipkart_products"


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
    --accent-bg: #f3efe7;        /* warm sand */
    --accent-bg-soft: #faf7f2;   /* lighter sand */
    --accent-border: #d6cfc2;
    --text-black: #000000;
}

/* App background */
.stApp {
    background: linear-gradient(135deg, #6fa8ff, #ff8a8a);
}

/* All text black */
* {
    color: var(--text-black) !important;
}

/* Headings */
h1, h2, h3, h4, h5 {
    color: var(--text-black) !important;
}

/* ----------------- SEARCH BAR ----------------- */
/* Centered search bar wrapper */
.search-wrapper {
    max-width: 440px;          /* slightly bigger */
    margin: 0 auto 24px auto;  /* center horizontally */
    background: none !important;
    padding: 0 !important;
}

/* Remove default background from parent container */
div[data-baseweb="input"] {
    background: none !important;
    width: 100% !important;
    max-width: 440px !important;
    margin: 0 auto !important;
}

/* Input inner box (white box) */
div[data-baseweb="input"] > div {
    border-radius: 12px;
    background-color: var(--accent-bg);  /* the white box */
    border: 1px solid var(--accent-border);
    padding: 4px 12px;                    /* padding inside box */
}

/* Input text */
div[data-baseweb="input"] input {
    color: var(--text-black) !important;
    caret-color: var(--text-black) !important;
    font-size: 16px;
    font-weight: 500;
}

/* Placeholder color */
div[data-baseweb="input"] input::placeholder {
    color: #333333 !important;
}

/* ----------------- BUTTONS ----------------- */
button[kind="primary"],
button[kind="secondary"],
button {
    background-color: var(--accent-bg) !important;
    color: var(--text-black) !important;
    border-radius: 10px !important;
    border: 1px solid var(--accent-border) !important;
    font-weight: 600 !important;
}

/* ----------------- CATEGORY CHIPS ----------------- */
.category-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 20px;
}
.category-chip {
    padding: 8px 16px;
    background: var(--accent-bg-soft);
    border: 1px solid var(--accent-border);
    border-radius: 999px;   /* fully oval */
    font-weight: 600;
    font-size: 14px;
    white-space: nowrap;
    cursor: pointer;
}
.category-chip:hover {
    background: var(--accent-bg);
    transform: translateY(-1px);
    transition: all 0.15s ease;
}

/* ----------------- PRODUCT CARDS ----------------- */
.product-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
}
.img-wrapper {
    height: 160px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin-bottom: 6px;
}
.img-wrapper img {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
}
.product-name {
    font-size: 14px;
    font-weight: 600;
    color: #000;
}
.product-brand,
.product-id {
    font-size: 12px;
    color: #666;
}
.product-price {
    font-size: 14px;
    font-weight: bold;
    color: #000;
    margin-top: 4px;
}

/* ----------------- PDP SINGLE PRODUCT ----------------- */
.pdp-container {
    max-width: 500px;       /* limits the white background */
    margin: 0 auto;          /* center horizontally */
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

/* ----------------- REMOVE STREAMLIT FOCUS GLOW ----------------- */
*:focus {
    outline: none !important;
    box-shadow: none !important;
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📌 Product Details")

    # PDP item in smaller centered container
    st.markdown(
        f"""
        <div class="pdp-container">
            <div class="img-wrapper">
                <img src="{item.get('item_image_url', '')}" />
            </div>
            <div class="product-name">{item.get('name', 'Unknown')}</div>
            <div class="product-brand">{item.get('brand', '')}</div>
            <div class="product-id">{item.get('product_id', '')}</div>
            <div class="product-price">₹ {item.get('discounted_price', '')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("🔁 You may also like")

    # Get recommendations
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

# -------- SEARCH --------
st.markdown("<br>", unsafe_allow_html=True)  # optional spacing

# Use 3 columns to center the input
col1, col2, col3 = st.columns([1, 2, 1])  # middle column wider

with col2:
    st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
    # Remove label, use placeholder only
    user_query = st.text_input("", placeholder="Search for products...")
    st.markdown('</div>', unsafe_allow_html=True)


if user_query:
    results = search_inventory(
        query=user_query,
        _from=0,
        size=20,
        model=model,
        INDEX_NAME=INDEX_NAME,
        es=es
    )

    st.subheader(f"Search Results ({len(results)})")
    render_results_grid(results)

# -------- BROWSE (VISIBLE WITHOUT SEARCH) --------
else:
    st.markdown("<h1>🛍️ Popular Categories</h1>", unsafe_allow_html=True)

    all_categories_with_counts = get_all_categories(es, INDEX_NAME)
    all_categories_with_counts = all_categories_with_counts[:25]

    chips_html = "<div class='category-container'>"
    for cat in all_categories_with_counts:
        chips_html += (
            f"<div class='category-chip'>"
            f"{cat['key']} ({cat['doc_count']})"
            f"</div>"
        )
    chips_html += "</div>"

    st.markdown(chips_html, unsafe_allow_html=True)

    browse_items = get_all_items(
        es=es,
        INDEX_NAME=INDEX_NAME,
        size=15
    )

    render_results_grid(browse_items)
