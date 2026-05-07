import streamlit as st
import webbrowser
from db.database import save_design, get_all_designs


def show_results():
    """Display generated design results with product recommendations."""
    
    if "current_design" not in st.session_state or not st.session_state["current_design"]:
        st.warning("Generate a design first!")
        if st.button("Go to Generate Page"):
            st.switch_page("pages/1_Generate.py")
        return
    
    design = st.session_state["current_design"]
    
    st.title("Your Room Design")
    
    st.subheader("Generated Room")
    
    if design.get("image_path"):
        if design["image_path"].startswith("http"):
            st.image(design["image_path"], use_container_width=True)
        else:
            try:
                st.image(design["image_path"], use_container_width=True)
            except:
                st.image(design["image_path"], use_container_width=True, channels="BGR")
    
    with st.expander("View Optimized Prompt"):
        st.text(design.get("optimized_prompt", ""))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Design", use_container_width=True):
            try:
                cart_items = []
                for item in design.get("cart", {}).get("items", []):
                    product = item.get("product") or {}
                    cart_items.append({
                        "product_id": product.get("id", ""),
                        "product_name": product.get("name", ""),
                        "category": product.get("category", ""),
                        "price": product.get("price", 0),
                        "allocated_budget": item.get("allocated_budget", 0),
                        "image_search_query": product.get("image_search_query", ""),
                        "purchase_url": product.get("purchase_url", "")
                    })
                
                saved_design = save_design(
                    design_data={
                        "prompt": design.get("original_prompt", ""),
                        "optimized_prompt": design.get("optimized_prompt", ""),
                        "style": design.get("style", ""),
                        "room_type": design.get("room_type", ""),
                        "budget": design.get("budget", 0),
                        "image_path": design.get("image_path", ""),
                        "total_cost": design.get("cart", {}).get("total_cost", 0),
                        "design_explanation": design.get("explanation", "")
                    },
                    cart_items=cart_items
                )
                st.success(f"Design saved! (ID: {saved_design.id})")
            except Exception as e:
                st.error(f"Error saving: {e}")
    
    with col2:
        if st.button("Regenerate", use_container_width=True):
            st.session_state["current_design"] = None
            st.switch_page("pages/1_Generate.py")
    
    st.divider()
    
    st.subheader("Design Analysis")
    
    with st.expander("View Design Explanation", expanded=True):
        st.write(design.get("explanation", ""))
    
    style_badge = design.get("style", "Modern")
    st.info(f"Detected Style: {style_badge}")
    
    st.divider()
    
    st.subheader("Recommended Furniture")
    
    cart = design.get("cart", {})
    
    total_budget = cart.get("total_budget", 0)
    total_cost = cart.get("total_cost", 0)
    savings = cart.get("savings", 0)
    over_budget_flag = cart.get("over_budget", False)
    
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Total Budget", f"₹{total_budget:,}")
    m2.metric("Estimated Cost", f"₹{total_cost:,}")
    
    if over_budget_flag:
        m3.metric("Over Budget", f"₹{total_cost - total_budget:,}", delta_color="inverse")
    else:
        m3.metric("Savings", f"₹{savings:,}", delta_color="normal")
    
    items = cart.get("items", [])
    
    if not items:
        st.info("No products found. Run `python data/seed_products.py` to enable product recommendations.")
    else:
        for item in items:
            product = item.get("product")
            category = item.get("category", product.get("category", "") if product else "")
            allocated = item.get("allocated_budget", 0)
            
            if not product:
                continue
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                
                with c1:
                    st.markdown(f"**{product.get('name', 'Unknown',)}</strong>")
                    st.caption(f"{product.get('brand', '')} | {product.get('category', '').replace('_', ' ').title()} | {product.get('style', '')}")
                    st.caption(f"{product.get('material', '')} | {product.get('color', '')}")
                
                with c2:
                    price = product.get("price", 0)
                    st.markdown(f"₹{price:,}")
                    if price > allocated:
                        st.warning(f"Over budget (₹{allocated:,} allocated)")
                    
                    if product.get("purchase_url"):
                        if st.button("View Product", key=f"view_{product.get('id')}"):
                            webbrowser.open(product["purchase_url"])
                
                with c3:
                    pass
    
    alternatives = cart.get("alternatives", {})
    if alternatives:
        with st.expander("Cheaper Alternatives Available"):
            for cat, alt in alternatives.items():
                if alt:
                    st.write(f"**{cat.title()}**: {alt.get('name', '')} - ₹{alt.get('price', 0):,}")
    
    st.divider()
    
    st.subheader("Refine Your Design")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    history = st.session_state["chat_history"]
    
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.write(content)
    
    suggested = ["Make it brighter", "Reduce total cost", "Add more storage", "Switch to darker tones"]
    
    st.caption("Suggested changes:")
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    
    for i, suggestion in enumerate(suggested):
        if i == 0:
            if sc1.button(suggestion, key=f"sugg_{i}"):
                history.append({"role": "user", "content": suggestion})
                st.rerun()
        elif i == 1:
            if sc2.button(suggestion, key=f"sugg_{i}"):
                history.append({"role": "user", "content": suggestion})
                st.rerun()
        elif i == 2:
            if sc3.button(suggestion, key=f"sugg_{i}"):
                history.append({"role": "user", "content": suggestion})
                st.rerun()
        else:
            if sc4.button(suggestion, key=f"sugg_{i}"):
                history.append({"role": "user", "content": suggestion})
                st.rerun()
    
    user_input = st.chat_input("Ask me to change anything...")
    
    if user_input:
        history.append({"role": "user", "content": user_input})
        
        try:
            from core.rag_assistant import RAGAssistant
            rag = RAGAssistant()
            response = rag.chat(
                message=user_input,
                history=history[:-1],
                design_context={
                    "style": design.get("style", ""),
                    "room_type": design.get("room_type", ""),
                    "budget": design.get("budget", 0),
                    "products": [item.get("product") for item in items if item.get("product")]
                }
            )
        except Exception:
            response = "I'm here to help refine your design. What would you like to change?"
        
        history.append({"role": "assistant", "content": response})
        st.session_state["chat_history"] = history
        st.rerun()