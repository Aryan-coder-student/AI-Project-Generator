import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
from typing import Optional
import base64

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
            You are an AI-powered freelance client simulation generator.
            
            🎯 Objective: Generate unique project briefs for the topic "{topic}"
            from the given context.
            ## Generation Parameters
            - Complexity Level: {complexity}
            - Number of Projects: {num_projects}
            
            <context>
            1. **Web Research Context**: {serpapi_data}
            2. **Academic Research Papers**: {papers_data}
            </context>
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
            - output in proper heading , subheading ,points.Like project heading should be in different fontsize and of same size of each project. 
            - ouput in only in markdown 
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
        page_title="CyberForge: AI Project Idea Generator",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Cyberpunk-Inspired Custom CSS
    st.markdown("""
    <style>
    /* Cyberpunk Background and Base Styling */
    .stApp {
        background-color: #0A0A1A;
        background-image: 
            linear-gradient(rgba(10, 10, 26, 0.9), rgba(10, 10, 26, 0.9)),
            repeating-linear-gradient(0deg, rgba(0, 255, 255, 0.03) 0px, rgba(0, 255, 255, 0.03) 1px, transparent 1px, transparent 4px);
        color: #00FFD4;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111127;
        border-right: 2px solid #00FFD4;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #00FFD4 !important;
        text-shadow: 0 0 10px rgba(0, 255, 212, 0.5);
    }

    /* Text Styling */
    .stMarkdown, .stTextArea, .stTextInput {
        color: #00FFD4 !important;
    }

    /* Button Cyberpunk Styling */
    .stButton>button {
        background-color: #FF1493 !important;
        color: black !important;
        border: 2px solid #00FFD4 !important;
        box-shadow: 0 0 10px rgba(255, 20, 147, 0.5);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00FFD4 !important;
        color: #0A0A1A !important;
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(0, 255, 212, 0.7);
    }

    /* Tabs Cyberpunk Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111127;
        border-bottom: 2px solid #00FFD4;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0A0A1A;
        color: #FF1493;
        border: 2px solid #FF1493;
        margin: 5px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #FF1493;
        color: #0A0A1A;
    }
    .stTabs [data-baseweb="tab"][data-selected="true"] {
        background-color: #00FFD4;
        color: #0A0A1A;
        border-color: #00FFD4;
    }

    /* Code Block Cyberpunk Styling */
    .stCodeBlock {
        background-color: #111127 !important;
        color: #00FFD4 !important;
        border: 2px solid #FF1493 !important;
    }

    /* Info and Error Boxes */
    .stAlert {
        background-color: #111127;
        color: #00FFD4;
        border: 2px solid #FF1493;
    }
    </style>
    """, unsafe_allow_html=True)

    # Cyberpunk Header
    st.markdown("<h1 style='text-align: center; color: #00FFD4; text-shadow: 0 0 10px rgba(0, 255, 212, 0.5);'>🌐 CyberForge: Project Nexus</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; color: #FF1493;'>
        Synthesize Innovative Project Vectors | AI-Powered Idea Generation Matrix
        </p>
    """, unsafe_allow_html=True)

    try:
        generator = ProjectIdeaGenerator()

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
                st.markdown("""
                ### 🔬 CyberForge Operational Protocols

                1. **Input Vector**: 
                   - Inject technological exploration domain
                   - Exemplars: "Quantum Interfaces", "Neuro-Computational Systems"

                2. **Configuration Calibration**:
                   - Modulate project generation density
                   - Adjust complexity synchronization level

                3. **Concept Initialization**:
                   - Activate "Concept Generator"
                   - AI synthesizes unique project matrices

                4. **Concept Exploration**:
                   - Visualize generated project vectors
                   - Export for further analysis

                #### Optimization Vectors:
                - Precision in input increases conceptual fidelity
                - Experiment with complexity modulation
                - Leverage data streams for refined ideation
                """)
        else:
            st.info("👈 Input exploration vector to activate CyberForge")

    except Exception as e:
        pass

    # Footer with cyberpunk flair
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #FF1493;'>
    Engineered in the Quantum Realm | Streamlit • LangChain • Groq Neural Network
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
