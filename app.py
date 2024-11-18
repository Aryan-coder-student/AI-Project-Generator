import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests

# Load environment variables
load_dotenv()

# Initialize API keys
serpapi_key = os.getenv("SERPAPI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="AI Project Idea Generator",
    page_icon="🚀",
    layout="wide",
)

# Application Header
st.title("🚀 AI Project Idea Generator")
st.markdown(
    """
Welcome to the **AI Project Idea Generator**!  
This tool leverages AI to help you discover innovative and practical project ideas based on your topic of interest.  
"""
)

# Initialize Resources
@st.cache_resource
def init_serpapi():
    return SerpAPIWrapper(serpapi_api_key=serpapi_key)

@st.cache_resource
def init_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        max_retries=2,
        api_key=groq_api_key
    )

# Helper Functions
def fetch_related_info(topic, serpapi):
    query = f"project ideas for {topic}"
    return serpapi.run(query)

def fetch_paperswithcode_data(topic):
    url = f"https://paperswithcode.com/api/v1/search/?q={topic}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        papers = data.get("results", [])
        if not papers:
            return "No papers found for the given topic."
        return "\n".join([
            f"{paper.get('paper', {}).get('title', 'No Title')}: {paper.get('paper', {}).get('url_abs', 'No URL')}"
            for paper in papers[:15]
        ])
    else:
        return f"API error with status code {response.status_code}"

# Load Resources
serpapi = init_serpapi()
llm = init_llm()

# Sidebar Inputs
with st.sidebar:
    st.header("🔧 Configuration")
    topic = st.text_area(
        "Enter your topic of interest:",
        placeholder="e.g., AI for sustainable agriculture, healthcare innovation",
        height=120,
    )
    number_of_projects = st.slider("Number of project ideas:", 1, 10, 5)
    project_complexity = st.select_slider(
        "Project Complexity Level:",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    generate_button = st.button("Generate Ideas 🎯")

# Tabs for Content
if topic:
    tab1, tab2 = st.tabs(["💡 Project Ideas", "📚 Resources"])

    with tab1:
        if generate_button:
            with st.spinner("Generating ideas..."):
                # Combine data for prompt
                combined_related_info = f"""
                1. Focus Topic: {topic}
                2. Complexity Level: {project_complexity}
                3. Research Highlights:
                   - Papers and Web Results will be displayed in the **Resources** tab.
                """
                # Generate Ideas
                st.subheader(f"🎯 Generated Project Ideas ({number_of_projects})")
                idea_prompt = PromptTemplate(
                    input_variables=["topic", "related_info", "number_of_projects"],
                    template="""
                    You are an AI project generator. Based on the topic "{topic}" and the following context:
                    {related_info}
                    Generate {number_of_projects} unique project ideas. Output Each idea :
                    - A title and brief description.
                    - Key implementation steps (data collection, model development, evaluation).
                    - Deployment strategy (e.g., web app, mobile app, API).
                    -Output with proper Markdown like make project title as Heading , also use underlines.
                    """
                )
                idea_chain = idea_prompt | llm
                result = idea_chain.invoke(input={
                    "topic": topic,
                    "related_info": combined_related_info,
                    "number_of_projects": number_of_projects
                })
                st.markdown(result.content)
                st.download_button(
                    label="📥 Download Ideas",
                    data=result.content,
                    file_name="project_ideas.md",
                    mime="text/markdown"
                )
        else:
            st.info("👈 Enter a topic in the sidebar and click **'Generate Ideas'** to get started!")

    with tab2:
        st.subheader("📚 Research Resources")
        with st.spinner("Fetching resources..."):
            serpapi_data = fetch_related_info(topic, serpapi)
            papers_data = fetch_paperswithcode_data(topic)

        st.markdown("### 🔍 Web Research Results")
        st.markdown(f"```\n{serpapi_data}\n```")

        st.markdown("### 📄 Research Papers")
        st.markdown(f"```\n{papers_data}\n```")
else:
    st.info("👈 Enter a topic in the sidebar to view resources and generate ideas.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using **Streamlit**, **LangChain**, and **Groq LLM**")
