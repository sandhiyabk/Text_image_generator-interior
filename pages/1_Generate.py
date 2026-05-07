import streamlit as st
import config
from core.prompt_optimizer import PromptOptimizer
from core.image_generator import ImageGenerator
from core.budget_optimizer import BudgetOptimizer
from core.rag_assistant import RAGAssistant


def generate_design():
    """Main design generation workflow."""
    
    st.header("Design Your Dream Room")
    
    with st.sidebar:
        st.subheader("Room Settings")
        
        room_type = st.selectbox(
            "Room Type",
            options=config.ROOM_TYPES,
            index=0
        )
        
        style = st.selectbox(
            "Style Preference",
            options=config.STYLES,
            index=0
        )
        
        budget_range = st.selectbox(
            "Budget Range",
            options=list(config.BUDGET_RANGES.keys()),
            index=1
        )
        budget = config.BUDGET_RANGES[budget_range]
        
        color_palette = st.text_input(
            "Color Palette (optional)",
            placeholder="e.g. warm whites, earthy tones"
        )
        
        with st.expander("Advanced Options"):
            custom_negative = st.text_input(
                "Negative Prompt Override",
                value="blurry, low quality, cartoon, anime, distorted, watermark, text"
            )
    
    st.subheader("Describe Your Room")
    
    example_prompts = [
        "A cozy living room with comfortable seating and natural light",
        "Minimalist bedroom with clean lines and storage",
        "Modern kitchen with open shelving and marble countertops",
        "Scandinavian dining space with wooden furniture"
    ]
    
    prompt = st.text_area(
        "What does your dream room look like?",
        height=150,
        placeholder="Describe your ideal room - furniture, colors, mood, activities..."
    )
    
    st.caption("Example: " + " | ".join([f'"{p[:30]}..."' for p in example_prompts[:3]]))
    
    col1, col2 = st.columns([2, 1])
    
    generate_button = col1.button(
        "Generate Design",
        type="primary",
        use_container_width=True
    )
    
    if generate_button:
        if not prompt:
            st.error("Please describe your room!")
            return
        
        with st.status("Creating your design...", expanded=True) as status:
            try:
                st.write("Optimizing your prompt...")
                
                optimizer = PromptOptimizer()
                optimized_prompt = optimizer.optimize(prompt, room_type, style, color_palette)
                
                st.write("Generating room design...")
                
                image_gen = ImageGenerator()
                image_path = image_gen.generate(optimized_prompt, custom_negative)
                
                if image_path.startswith("https"):
                    if not config.REPLICATE_API_TOKEN or config.REPLICATE_API_TOKEN == "your_replicate_api_token_here":
                        st.warning("Add REPLICATE_API_TOKEN to .env for real image generation")
                
                st.write("Finding matching furniture...")
                
                budget_opt = BudgetOptimizer()
                cart = budget_opt.build_cart(budget, room_type, style, image_path)
                
                st.write("Creating design explanation...")
                
                products = []
                for item in cart.get("items", []):
                    if item.get("product"):
                        products.append(item["product"])
                
                rag = RAGAssistant()
                explanation = rag.explain_design(prompt, style, room_type, products)
                
                status.update(label="Design ready!", state="complete")
                
                st.session_state["current_design"] = {
                    "original_prompt": prompt,
                    "optimized_prompt": optimized_prompt,
                    "style": style,
                    "room_type": room_type,
                    "budget": budget,
                    "image_path": image_path,
                    "cart": cart,
                    "explanation": explanation
                }
                
                st.session_state["chat_history"] = []
                
                st.success("Design ready!")
                st.switch_page("pages/2_Results.py")
                
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error")
                st.error(f"Something went wrong: {str(e)}")