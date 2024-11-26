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

# Project Idea Generator Class
class ProjectIdeaGenerator:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.serpapi_key or not self.groq_api_key:
            raise ValueError("Missing required API keys in .env file")
        
        self.serpapi = self._init_serpapi()
        self.llm = self._init_llm()

    def _init_serpapi(self):
        return SerpAPIWrapper(serpapi_api_key=self.serpapi_key)

    def _init_llm(self):
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_retries=2,
            api_key=self.groq_api_key
        )

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_related_info(topic: str, serpapi_key: str) -> str:
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
                input_variables=["topic", "complexity", "num_projects", "serpapi_data", "papers_data"],
                template="""
                    🎯 Generate project ideas for the topic "{topic}" with the complexity level: {complexity}.
                    Context from web: {serpapi_data}
                    Context from papers: {papers_data}
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
    # Page Configuration with a dark theme
    st.set_page_config(
        page_title="AI Project Idea Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS Styling
    st.markdown("""
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #F1F1F1;
            }
            .main {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            .sidebar {
                background-color: #1f2a40;
                color: white;
            }
            h1 {
                color: #4CAF50;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 12px;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header and Introduction
    st.title("🚀 AI Project Idea Generator")
    st.markdown("""
        Welcome to the **AI Project Idea Generator**!  
        Discover innovative project ideas with insights from web research and academic papers.  
        Customize the complexity and number of ideas to suit your needs.  
    """)

    try:
        generator = ProjectIdeaGenerator()

        # Sidebar Inputs with improved styling
        with st.sidebar:
            st.header("🔧 Configuration")
            topic = st.text_area(
                "Enter your topic of interest:",
                placeholder="e.g., AI for sustainable agriculture, healthcare innovation",
                height=120,
                max_chars=150
            )
            number_of_projects = st.slider("Number of project ideas:", 1, 10, 5)
            project_complexity = st.select_slider(
                "Project Complexity Level:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate"
            )
            generate_button = st.button("Generate Ideas 🎯")

        if topic:
            tab1, tab2 = st.tabs(["💡 Project Ideas", "📚 Research Resources"])
            
            with tab1:
                if generate_button:
                    with st.spinner("Generating ideas..."):
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
                            st.subheader(f"🎯 Generated Project Ideas ({number_of_projects})")
                            st.markdown(result)
                            
                            st.download_button(
                                label="📥 Download Ideas",
                                data=result,
                                file_name="project_ideas.md",
                                mime="text/markdown"
                            )
                else:
                    st.info("👈 Enter a topic and click **'Generate Ideas'** to get started!")

            with tab2:
                st.subheader("📚 Research Resources")
                
                if serpapi_data:
                    st.markdown("### 🔍 Web Research Results")
                    st.markdown(f"```\n{serpapi_data}\n```")
                
                if papers_data:
                    st.markdown("### 📄 Research Papers")
                    st.markdown(papers_data)

        else:
            st.info("👈 Enter a topic in the sidebar to view resources and generate ideas.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your API keys and try again.")

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using **Streamlit**, **LangChain**, and **Groq LLM**")

if __name__ == "__main__":
    main()
