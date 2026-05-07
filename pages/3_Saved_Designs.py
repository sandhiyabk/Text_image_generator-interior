import streamlit as st
from datetime import datetime
from db.database import get_all_designs, delete_design


def show_saved_designs():
    """Display saved designs gallery."""
    
    st.title("Saved Designs")
    
    try:
        designs = get_all_designs()
    except Exception as e:
        st.error(f"Error loading designs: {e}")
        designs = []
    
    if not designs:
        st.info("No saved designs yet!")
        
        if st.button("Create Your First Design"):
            st.switch_page("pages/1_Generate.py")
        return
    
    st.write(f"**{len(designs)} saved design(s)")
    
    cols_per_row = 3
    rows = [designs[i:i + cols_per_row] for i in range(0, len(designs), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        
        for i, design in enumerate(row):
            with cols[i]:
                with st.container(border=True):
                    image_path = design.get("image_path", "")
                    
                    if image_path:
                        if image_path.startswith("http"):
                            st.image(image_path, use_container_width=True)
                        else:
                            try:
                                st.image(image_path, use_container_width=True)
                            except:
                                st.image(image_path, use_container_width=True, channels="BGR")
                    else:
                        st.image("https://placehold.co/400x300/e8d5b7/8B4513?text=No+Image", use_container_width=True)
                    
                    room_type = design.get("room_type", "Room")
                    style = design.get("style", "Modern")
                    st.markdown(f"**{room_type} - {style}**")
                    
                    budget = design.get("budget", 0)
                    total_cost = design.get("total_cost", 0)
                    st.caption(f"Budget: ₹{budget:,} | Cost: ₹{total_cost:,}")
                    
                    created = design.get("created_at")
                    if created:
                        if hasattr(created, "strftime"):
                            date_str = created.strftime("%Y-%m-%d")
                        else:
                            date_str = str(created)[:10]
                        st.caption(f"Created: {date_str}")
                    
                    with st.expander("View Details"):
                        st.write("**Products:**")
                        
                        cart_items = design.get("cart_items", [])
                        for item in cart_items:
                            st.write(f"- {item.get('product_name', 'Unknown')} - ₹{item.get('price', 0):,}")
                        
                        explanation = design.get("design_explanation", "")
                        if explanation:
                            st.write("**Explanation:**")
                            st.text(explanation[:300] + "..." if len(explanation) > 300 else explanation)
                    
                    if st.button("Delete", key=f"del_{design['id']}"):
                        try:
                            delete_design(design["id"])
                            st.success("Design deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting: {e}")
    
    st.divider()
    
    st.subheader("Export")
    
    if st.button("Export as Text Report"):
        report_lines = []
        
        for design in designs:
            report_lines.append("=" * 50)
            report_lines.append(f"Design: {design['room_type']} - {design['style']}")
            report_lines.append("=" * 50)
            report_lines.append(f"Created: {design.get('created_at', 'N/A')}")
            report_lines.append(f"Budget: ₹{design.get('budget', 0):,}")
            report_lines.append(f"Estimated Cost: ₹{design.get('total_cost', 0):,}")
            report_lines.append("")
            report_lines.append("Original Prompt:")
            report_lines.append(design.get("prompt", ""))
            report_lines.append("")
            report_lines.append("Products:")
            
            for item in design.get("cart_items", []):
                report_lines.append(f"  - {item.get('product_name')} - ₹{item.get('price'):,}")
            
            report_lines.append("")
            report_lines.append("Design Explanation:")
            report_lines.append(design.get("design_explanation', ""))
            report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        st.download_button(
            label="Download Report",
            data=report_text,
            file_name="interior_designs_report.txt",
            mime="text/plain"
        )