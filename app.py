import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional

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
            template="""
            You are an AI-powered project idea generator.
            
            🎯 Objective: Generate unique project briefs for the topic "{topic}"
            
            ## Generation Parameters
            - Complexity Level: {complexity}
            - Number of Projects: {num_projects}
            
            ## Context Sources
            1. **Web Research Context**: {serpapi_data}
            2. **Academic Research Papers**: {papers_data}
            
            ## Project Brief Requirements
            
            ### 1. Descriptive Title
            - Format: Markdown Heading (H2)
            - Capture project essence concisely
            
            ### 2. Problem Statement
            - Written in authentic innovator's voice
            - Include:
            * Specific technological challenge
            * Potential impact
            * Innovative approach
            
            ### 3. Key Deliverables
            - Explicitly list expected project outcomes
            - Ensure clarity and technical depth
            
            ### 4. Project Scope and Constraints
            - Estimated development timeline
            - Potential technological challenges
            - Recommended skill set
            
            ### 5. Innovative Techniques
            - Cutting-edge methodologies
            - Potential technological approaches
            
            ## Output: 
            - Markdown for enhanced readability
            - Add a divider after every project
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
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }
    .sidebar {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1.5rem;
    }
    .stButton > button {
        background-color: #4B0082 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stButton > button:hover {
        background-color: #6A5ACD !important;
    }
    .title-container {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .title-container img {
        margin-right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Page Configuration
    st.set_page_config(
        page_title="🚀 InnovaAI: Project Idea Generator",
        page_icon="🚀",
        layout="wide",
    )

    # Application Header
    st.markdown("""
    <div class="title-container">
        <img src="https://img.icons8.com/nolan/64/rocket.png" alt="Rocket Icon">
        <h1>InnovaAI: Project Idea Generator</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Welcome to **InnovaAI**! 🌟 
    Discover cutting-edge project ideas powered by artificial intelligence. 
    Enter a topic and let our AI help you brainstorm innovative concepts.
    """)

    try:
        generator = ProjectIdeaGenerator()

        # Sidebar Inputs
        with st.sidebar:
            st.header("🔧 Project Configuration")
            
            # Topic Input with Enhanced Styling
            topic = st.text_area(
                "Enter your topic of interest:",
                placeholder="e.g., AI for climate change, quantum computing, sustainable tech",
                height=150,
                help="Be specific to get more targeted project ideas!"
            )

            # Complexity Selector with Custom Styling
            project_complexity = st.select_slider(
                "Project Complexity:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate",
                help="Choose the technical complexity of your project ideas"
            )

            # Number of Projects Slider
            number_of_projects = st.slider(
                "Number of Project Ideas:", 
                min_value=1, 
                max_value=10, 
                value=5,
                help="Select how many unique project ideas you want to generate"
            )

            # Generate Button with Enhanced Interaction
            generate_button = st.button(
                "Generate Innovative Ideas 💡", 
                help="Click to unleash AI-powered project creativity!"
            )

        # Main Content Area with Tabs
        if topic:
            tab1, tab2 = st.tabs(["💡 Generated Ideas", "🔍 Research Insights"])
            
            with tab1:
                if generate_button:
                    with st.spinner("Generating innovative project ideas..."):
                        # Fetch supplementary data
                        serpapi_data = ProjectIdeaGenerator.fetch_related_info(topic, generator.serpapi_key)
                        papers_data = ProjectIdeaGenerator.fetch_paperswithcode_data(topic)
                        
                        # Generate project ideas
                        result = generator.generate_ideas(
                            topic=topic,
                            complexity=project_complexity,
                            num_projects=number_of_projects,
                            serpapi_data=serpapi_data,
                            papers_data=papers_data
                        )
                        
                        if result:
                            st.subheader(f"🚀 AI-Generated Project Ideas for {topic}")
                            st.markdown(result)
                            
                            # Download Button with Enhanced Styling
                            st.download_button(
                                label="📥 Download Project Ideas",
                                data=result,
                                file_name="innovative_project_ideas.md",
                                mime="text/markdown",
                                help="Download your AI-generated project ideas"
                            )
                else:
                    st.info("👈 Configure your project parameters in the sidebar and click 'Generate Innovative Ideas'!")

            with tab2:
                st.subheader("🔬 Research Context")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if serpapi_data:
                        st.markdown("#### 🌐 Web Research Insights")
                        st.code(serpapi_data, language="text")
                
                with col2:
                    if papers_data:
                        st.markdown("#### 📄 Academic Research Papers")
                        st.markdown(papers_data)
        else:
            st.info("👈 Enter a topic in the sidebar to generate innovative project ideas!")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please check your configuration and try again.")

    # Footer with Tech Attribution
    st.markdown("---")
    st.markdown("Crafted with ❤️ using **Streamlit**, **LangChain**, and **Groq LLM**")

if __name__ == "__main__":
    main()
