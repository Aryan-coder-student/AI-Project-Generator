import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional
import time

# Custom CSS for modern, clean UI
def apply_custom_styling():
    st.markdown("""
    <style>
        /* Global App Styling */
        .stApp {
            background-color: #f4f6f9;
            font-family: 'Inter', 'Roboto', sans-serif;
        }
        
        /* Sidebar Enhancements */
        .css-1aumxhk {
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        /* Button Styling */
        .stButton>button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            transform: scale(1.05);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        
        /* Input and Text Area Styling */
        .stTextArea textarea {
            border: 2px solid #e0e4eb;
            border-radius: 10px;
            padding: 12px;
            background-color: #f9fafb;
        }
        
        /* Slider Styling */
        .stSlider > div > div > div > div {
            background-color: #3b82f6;
            border-radius: 10px;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f4f6f9;
            border-radius: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #4b5563;
            padding: 10px 15px;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

class ProjectIdeaGenerator:
    def __init__(self):
        load_dotenv()
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.serpapi_key or not self.groq_api_key:
            raise ValueError("🚨 Missing API keys. Please check your .env file.")
        
        self.serpapi = SerpAPIWrapper(serpapi_api_key=self.serpapi_key)
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_retries=2,
            api_key=self.groq_api_key
        )

def main():
    # Page Configuration with Enhanced Styling
    st.set_page_config(
        page_title="🚀 AI Project Idea Generator",
        page_icon="🚀",
        layout="wide",
    )
    
    # Apply Custom Styling
    apply_custom_styling()

    # Enhanced Header with Gradient and Animation
    st.markdown("""
    <div style='background: linear-gradient(90deg, #3b82f6, #7c3aed);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5em;
                font-weight: 800;
                text-align: center;
                margin-bottom: 20px;
                animation: gradient-animation 3s ease infinite;'>
        AI Project Idea Generator
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with Enhanced Layout
    with st.sidebar:
        st.header("🔧 Project Configuration")
        
        # Topic Input with Placeholder and Validation
        topic = st.text_area(
            "Enter your topic of interest:",
            placeholder="e.g., AI for sustainable agriculture, healthcare innovation",
            height=120
        )
        
        # Complexity Selector with Tooltips
        project_complexity = st.select_slider(
            "Project Complexity Level 🧩",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )
        
        # Informative Complexity Tooltip
        st.info("""
        🔍 Complexity Guide:
        • Beginner: Simple projects
        • Intermediate: Moderate challenges
        • Advanced: Cutting-edge concepts
        """)
        
        # Number of Projects Slider with Enhanced Style
        number_of_projects = st.slider(
            "Number of Project Ideas", 
            1, 10, 5, 
            help="Select how many project ideas you want to generate"
        )
        
        # Generate Button with Engaging Style
        generate_button = st.button("Generate Ideas 🎯", use_container_width=True)

    # Main Content Area
    if topic and generate_button:
        # Input Validation
        if len(topic.strip()) < 3:
            st.warning("🚨 Please enter a more specific topic (min 3 characters)")
        else:
            # Tabs for organized display
            tab1, tab2 = st.tabs(["💡 Project Ideas", "📚 Research Resources"])
            
            with tab1:
                with st.spinner("🧠 Generating innovative project ideas..."):
                    # Simulated loading for better UX
                    time.sleep(1)
                    
                    # Rest of your existing generation logic here
                    # ... (keep your existing ProjectIdeaGenerator methods)

    # Footer with Modern Design
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280;'>
        Crafted with ❤️ using 
        <strong style='color: #3b82f6;'>Streamlit</strong> | 
        <strong style='color: #7c3aed;'>LangChain</strong> | 
        <strong style='color: #10b981;'>Groq LLM</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
