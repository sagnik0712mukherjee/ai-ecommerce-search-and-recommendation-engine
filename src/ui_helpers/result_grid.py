import streamlit as st

def render_results_grid(items, cols=5):
    if not items:
        st.info("No items to display")
        return

    rows = [items[i:i + cols] for i in range(0, len(items), cols)]

    for row_idx, row in enumerate(rows):
        columns = st.columns(cols)

        for col_idx, item in enumerate(row):
            item = item.get("_source", item)

            unique_key = (
                item.get("product_id")
                or f"{item.get('name', 'item')}_{row_idx}_{col_idx}"
            )

            with columns[col_idx]:
                st.markdown(
                    f"""
                    <div class="product-card">
                        <div class="img-wrapper">
                            <img src="{item.get('item_image_url', '')}" />
                        </div>
                        <div class="product-name">{item.get('name', 'Unknown')[:35]}...</div>
                        <div class="product-brand">{item.get('brand', '')}</div>
                        <div class="product-id">{item.get('product_id', '')}</div>
                        <div class="product-price">₹ {item.get('discounted_price', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "Open",
                    key=f"open_{unique_key}",
                    use_container_width=True
                ):
                    st.session_state.selected_item = item
                    st.session_state.view = "PDP"
                    st.rerun()
