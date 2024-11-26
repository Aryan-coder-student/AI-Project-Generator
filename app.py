import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional

load_dotenv()
serpapi_data = {}

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
            You are an AI-powered freelance client simulation generator.
            
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
            - Written in authentic client voice
            - Include:
            * Specific need
            * Underlying motivation
            * Clear expectations
            
            ### 3. Key Deliverables
            - Explicitly list expected outcomes
            - Ensure clarity and measurability
            
            ### 4. Project Scope and Constraints
            - Timeline specifications
            - Budget limitations
            - Platform or technology preferences
            
            ### 5. Recommended Tools/Techniques
            - Client-suggested methodologies
            - Preferred technological approach
            
            ## Output: 
            - Markdown for enhanced readability
            - Add A divider after every project
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
    # Page Configuration
    st.set_page_config(
        page_title="AI Project Idea Generator",
        page_icon="🚀",
        layout="wide",
    )

    # Application Header
    st.title("🚀 AI Project Idea Generator")
    st.markdown("""
        Welcome to the **AI Project Idea Generator**!  
        This tool leverages AI to help you discover innovative and practical project ideas based on your topic of interest.  
    """)

    try:
        generator = ProjectIdeaGenerator()

        # Sidebar Inputs with enhanced styling
        with st.sidebar:
            st.header("🔧 Configuration")
            topic = st.text_area(
                "Enter your topic of interest:",
                placeholder="e.g., AI for sustainable agriculture, healthcare innovation",
                height=120,
                label_visibility="collapsed"
            )
            number_of_projects = st.slider("Number of project ideas:", 1, 10, 5)
            project_complexity = st.select_slider(
                "Project Complexity Level:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate"
            )
            generate_button = st.button("Generate Ideas 🎯")

        if topic:
            tab1, tab2 = st.tabs(["💡 Project Ideas", "📚 Resources"])
            
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
                    st.info("👈 Enter a topic in the sidebar and click **'Generate Ideas'** to get started!")

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

    # Footer with clean styling
    st.markdown("---")
    st.markdown("Built with ❤️ using **Streamlit**, **LangChain**, and **Groq LLM**")

if __name__ == "__main__":
    main()
