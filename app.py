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

def get_base64_of_bin_file(bin_file):
    """Convert image to base64"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    """Set background image for Streamlit app"""
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def main():
    # Page Configuration
    st.set_page_config(
        page_title="InnoVate: AI Project Idea Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Optional Background (comment out if no background image)
    # Ensure you have a background image file in your project directory
    # set_background('background.png')  # Uncomment and add your background image

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
        color: #2C3E50;
    }
    .stButton>button {
        color: white;
        background-color: #3498DB;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980B9;
        transform: scale(1.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: #ECF0F1;
        color: #2C3E50;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3498DB;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Application Header with enhanced styling
    st.markdown("<h1 style='text-align: center; color: #2C3E50;'>🚀 InnoVate: AI Project Idea Generator</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; color: #7F8C8D;'>
        Unlock innovative project ideas powered by AI, web research, and academic insights.
        </p>
    """, unsafe_allow_html=True)

    try:
        generator = ProjectIdeaGenerator()

        # Sidebar with enhanced styling
        with st.sidebar:
            st.header("🔧 Project Configuration")
            
            # Topic input with placeholder and helper text
            topic = st.text_area(
                "Topic of Interest",
                placeholder="e.g., AI for sustainable agriculture, healthcare innovation",
                help="Enter a broad or specific topic to generate project ideas",
                height=150
            )
            
            # Advanced configuration with tooltips
            col1, col2 = st.columns(2)
            with col1:
                number_of_projects = st.slider(
                    "Number of Ideas", 1, 10, 5, 
                    help="Select how many project ideas you want to generate"
                )
            
            with col2:
                project_complexity = st.selectbox(
                    "Complexity Level",
                    ["Beginner", "Intermediate", "Advanced"],
                    index=1,
                    help="Choose the technical complexity of project ideas"
                )
            
            # Stylized generate button
            generate_button = st.button("🎯 Generate Ideas", use_container_width=True)

        # Main content area with tabs
        if topic:
            tab1, tab2, tab3 = st.tabs(["💡 Project Ideas", "🔍 Research Insights", "📋 Instructions"])
            
            with tab1:
                if generate_button:
                    with st.spinner("🧠 Generating innovative project ideas..."):
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
                            st.subheader(f"🚀 {number_of_projects} Unique Project Ideas")
                            st.markdown(result)
                            
                            # Enhanced download button with icon
                            st.download_button(
                                label="📥 Download Project Ideas",
                                data=result,
                                file_name=f"{topic.replace(' ', '_')}_project_ideas.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                else:
                    st.info("👈 Configure your project parameters in the sidebar and click 'Generate Ideas'!")

            with tab2:
                st.subheader("🔬 Research Context")
                
                col1, col2 = st.columns(2)
                with col1:
                    if serpapi_data:
                        st.markdown("### 🌐 Web Research")
                        st.code(serpapi_data, language="text")
                
                with col2:
                    if papers_data:
                        st.markdown("### 📄 Academic Papers")
                        st.markdown(papers_data)

            with tab3:
                st.markdown("""
                ### 🎓 How to Use InnoVate

                1. **Enter Topic**: 
                   - Provide a broad or specific area of interest
                   - Examples: "AI", "Sustainable Technology", "Healthcare Innovation"

                2. **Configure Options**:
                   - Choose number of project ideas
                   - Select complexity level

                3. **Generate Ideas**:
                   - Click "Generate Ideas" button
                   - AI generates unique, context-aware project briefs

                4. **Explore Results**:
                   - View project ideas in markdown format
                   - Download ideas for later reference

                #### Pro Tips:
                - More specific topics yield more targeted ideas
                - Experiment with different complexity levels
                - Use research insights to refine your project concept
                """)
        else:
            st.info("👈 Enter a topic in the sidebar to explore project ideas!")

    except Exception as e:
        st.error(f"🚨 An unexpected error occurred: {str(e)}")
        st.info("Please check your API keys and try again.")

    # Footer with attribution
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7F8C8D;'>
    Built with ❤️ using Streamlit, LangChain, and Groq LLM
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
