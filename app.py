import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional

# Load environment variables
load_dotenv()

class ProjectIdeaGenerator:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.serpapi_key or not self.groq_api_key:
            raise ValueError("Missing required API keys in .env file")
        
        # Initialize resources directly in constructor
        self.serpapi = self._init_serpapi()
        self.llm = self._init_llm()

    def _init_serpapi(self):
        """Initialize SerpAPI wrapper"""
        return SerpAPIWrapper(serpapi_api_key=self.serpapi_key)

    def _init_llm(self):
        """Initialize Groq LLM"""
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_retries=2,
            api_key=self.groq_api_key
        )

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_related_info(topic: str, serpapi_key: str) -> str:
        """Fetch related information using SerpAPI"""
        try:
            serpapi = SerpAPIWrapper(serpapi_api_key=serpapi_key)
            query = f"project ideas for {topic}"
            return serpapi.run(query)
        except Exception as e:
            st.error(f"Error fetching related information: {str(e)}")
            return ""

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_paperswithcode_data(topic: str) -> str:
        """Fetch papers from Papers with Code API"""
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
        """Generate project ideas using the LLM"""
        try:
            idea_prompt = PromptTemplate(
                input_variables=[
                    "topic", 
                    "complexity", 
                    "num_projects", 
                    "serpapi_data", 
                    "papers_data"
                ],
                template="""Your prompt template here"""
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
    # Page Configuration
    st.set_page_config(
        page_title="CyberForge: AI Project Idea Generator",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Cyberpunk-Inspired Custom CSS
    st.markdown("""<style>/* Your CSS here */</style>""", unsafe_allow_html=True)

    # Cyberpunk Header
    st.markdown("<h1 style='text-align: center; color: #00FFD4;'>🌐 CyberForge: Project Nexus</h1>", unsafe_allow_html=True)

    try:
        generator = ProjectIdeaGenerator()

        # Initialize `serpapi_data` and `papers_data` to default values
        serpapi_data = ""
        papers_data = ""

        # Sidebar with cyberpunk theme
        with st.sidebar:
            st.header("🔧 Project Configuration Node")
            
            # Topic input 
            topic = st.text_area(
                "Input Exploration Vector",
                placeholder="e.g., Quantum AI, Neuro-Augmented Systems",
                help="Enter technological domain for project synthesis",
                height=150
            )
            
            # Configuration columns
            col1, col2 = st.columns(2)
            with col1:
                number_of_projects = st.slider(
                    "Idea Generation Density", 1, 10, 5, 
                    help="Calibrate project ideation intensity"
                )
            
            with col2:
                project_complexity = st.selectbox(
                    "Complexity Modulation",
                    ["Novice Protocol", "Intermediate Sync", "Advanced Nexus"],
                    index=1,
                    help="Adjust technological complexity parameters"
                )
            
            # Generate button
            generate_button = st.button("🚀 Initialize Concept Generator", use_container_width=True)

        # Main content area
        if topic:
            tab1, tab2, tab3 = st.tabs(["💡 Concept Matrices", "🔍 Data Streams", "📋 Operational Protocols"])
            
            with tab1:
                if generate_button:
                    with st.spinner("🌐 Synthesizing Innovative Project Vectors..."):
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
                            st.subheader(f"🚀 {number_of_projects} Concept Matrices Generated")
                            st.markdown(result)
                            
                            # Download button
                            st.download_button(
                                label="💾 Export Concept Matrices",
                                data=result,
                                file_name=f"cyberforge_{topic.replace(' ', '_')}_concepts.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                else:
                    st.info("👈 Configure project parameters and initiate concept generation!")

            with tab2:
                st.subheader("🌐 Information Streams")
                
                col1, col2 = st.columns(2)
                with col1:
                    if serpapi_data:
                        st.markdown("### 📡 Web Data Nexus")
                        st.code(serpapi_data, language="text")
                
                with col2:
                    if papers_data:
                        st.markdown("### 📄 Academic Transmission")
                        st.markdown(papers_data)

            with tab3:
                st.markdown("Your protocol here")

        else:
            st.info("👈 Input exploration vector to activate CyberForge")

    except Exception as e:
        st.error(f"🚨 System Anomaly Detected: {str(e)}")
        st.info("Verify system configurations and reinitialize")

if __name__ == "__main__":
    main()
