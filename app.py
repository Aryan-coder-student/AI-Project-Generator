import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional
import base64

# Custom CSS for enhanced styling
def local_css():
    st.markdown("""
    <style>
    .main-container {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stApp {
        background-color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .metric-container {
        background-color: #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

class ProjectIdeaGenerator:
    def __init__(self):
        load_dotenv()
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.serpapi_key or not self.groq_api_key:
            raise ValueError("Missing required API keys in .env file")
        
        self.serpapi = SerpAPIWrapper(serpapi_api_key=self.serpapi_key)
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_retries=2,
            api_key=self.groq_api_key
        )

    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_related_info(topic: str, serpapi_key: str) -> str:
        try:
            serpapi = SerpAPIWrapper(serpapi_api_key=serpapi_key)
            query = f"project ideas for {topic}"
            return serpapi.run(query)
        except Exception as e:
            st.error(f"Error fetching related information: {str(e)}")
            return ""

    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_paperswithcode_data(topic: str) -> str:
        try:
            url = f"https://paperswithcode.com/api/v1/search/?q={topic}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get("results", [])
            
            if not papers:
                return "No papers found for the given topic."
                
            return "\n".join([
                f"- {paper.get('paper', {}).get('title', 'No Title')}\n  {paper.get('paper', {}).get('url_abs', 'No URL')}"
                for paper in papers[:15]
            ])
        except requests.RequestException as e:
            st.error(f"Error fetching papers: {str(e)}") 
            return "Failed to fetch papers. Please try again later."

    def generate_ideas(self, topic: str, complexity: str, num_projects: int, 
                      serpapi_data: str, papers_data: str) -> Optional[str]:
        try:
            idea_prompt = PromptTemplate(
                input_variables=[
                    "topic", 
                    "complexity", 
                    "num_projects", 
                    "serpapi_data", 
                    "papers_data"
                ],
                template="""
                🚀 AI Project Idea Generator Prompt

                Topic: {topic}
                Complexity: {complexity}
                Number of Projects: {num_projects}

                Context:
                - Web Research: {serpapi_data}
                - Academic Papers: {papers_data}

                Generate unique, innovative project briefs with:
                1. Catchy Title
                2. Problem Statement
                3. Key Deliverables
                4. Project Constraints
                5. Recommended Tools
                """
            )
            
            chain_result = idea_prompt | self.llm
            
            return chain_result.invoke(input={
                "topic": topic,
                "complexity": complexity,
                "num_projects": num_projects,
                "serpapi_data": serpapi_data,
                "papers_data": papers_data
            }).content
        except Exception as e:
            st.error(f"Error generating ideas: {str(e)}")
            return None

def main():
    # Enhanced Page Configuration
    st.set_page_config(
        page_title="🚀 Innovative Project Idea Lab",
        page_icon="🔬",
        layout="wide",
    )

    # Custom CSS
    local_css()

    # Application Header with Animated Background
    st.markdown("""
    <div class="main-container">
        <h1 style="color: #2c3e50; text-align: center;">🔬 Innovative Project Idea Lab</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Unlock creativity with AI-powered project inspiration
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        generator = ProjectIdeaGenerator()

        # Sidebar with Enhanced Design
        with st.sidebar:
            st.markdown("## 🛠️ Project Configuration")
            
            with st.expander("📝 Topic Details", expanded=True):
                topic = st.text_area(
                    "Enter your topic of interest:",
                    placeholder="AI in healthcare, sustainable tech...",
                    height=100,
                )

            with st.expander("⚙️ Customization", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    number_of_projects = st.slider(
                        "Number of Ideas:", 
                        1, 10, 5, 
                        help="Choose how many project ideas to generate"
                    )
                with col2:
                    project_complexity = st.select_slider(
                        "Complexity Level:",
                        options=["Beginner", "Intermediate", "Advanced"],
                        value="Intermediate",
                        help="Select the project difficulty"
                    )

            generate_button = st.button("✨ Generate Ideas", use_container_width=True)

        if topic:
            tab1, tab2, tab3 = st.tabs(["💡 Project Ideas", "🔍 Research", "📊 Metrics"])
            
            with tab1:
                if generate_button:
                    with st.spinner("🧠 AI is brewing innovative ideas..."):
                        serpapi_data = ProjectIdeaGenerator.fetch_related_info(topic, generator.serpapi_key)
                        papers_data = ProjectIdeaGenerator.fetch_paperswithcode_data(topic)
                        
                        result = generator.generate_ideas(
                            topic=topic,
                            complexity=project_complexity,
                            num_projects=number_of_projects,
                            serpapi_data=serpapi_data,
                            papers_data=papers_data
                        )
                        
                        if result:
                            st.markdown("## 🚀 Generated Project Ideas")
                            st.markdown(result)
                            
                            st.download_button(
                                label="📥 Download Project Ideas",
                                data=result,
                                file_name="project_ideas.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                else:
                    st.info("👈 Configure your project parameters and click **Generate Ideas**")

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 🔍 Web Research")
                    if serpapi_data:
                        st.code(serpapi_data)
                
                with col2:
                    st.markdown("### 📄 Academic Papers")
                    if papers_data:
                        st.markdown(papers_data)

            with tab3:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("🎯 Ideas Generated", number_of_projects)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("📊 Complexity", project_complexity)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("🌐 Topic", topic[:20] + "..." if len(topic) > 20 else topic)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Enter a topic in the sidebar to begin your project discovery journey!")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("🔧 Please check your configuration and try again.")

    # Enhanced Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d;">
        Crafted with 💖 using Streamlit, LangChain, and Groq
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
