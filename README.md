
# 🚀 AI Project Idea Generator

The **AI Project Idea Generator** is a Streamlit-based application designed to inspire innovative project ideas using advanced AI technologies like LangChain, Groq LLM, and SerpAPI. Simply input a topic of interest, and the app will provide tailored project ideas, implementation steps, and research resources.

---

## Features
- **Generate AI Project Ideas**:
  - Provides creative project titles and descriptions.
  - Suggests implementation steps (e.g., data collection, model development).
  - Recommends deployment strategies (e.g., web apps, APIs).

- **Research Integration**:
  - Fetches related web results using **SerpAPI**.
  - Pulls academic resources from **Papers with Code**.

- **Customizable Outputs**:
  - Choose the number of ideas and complexity level (Beginner, Intermediate, Advanced).

---

## Requirements

Before running the application, ensure you have the following installed:
- Python 3.8 or later
- Required Python libraries (see `requirements.txt`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-project-idea-generator.git
   cd ai-project-idea-generator
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   SERPAPI_API_KEY=your_serpapi_key
   GROQ_API_KEY=your_groq_api_key
   ```

---

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to the URL provided by Streamlit (default: `http://localhost:8501`).

3. Enter a topic of interest in the sidebar, configure options, and click **Generate Ideas 🎯**.

---

## Outputs

### Tabs:
1. **💡 Project Ideas**: Displays generated ideas with detailed steps and deployment strategies.
2. **📚 Resources**: Shows research highlights from web search and academic papers.

### Download Options:
- Export project ideas in Markdown format using the **Download Ideas** button.

---

## Example

### Input:
**Topic**: AI for sustainable agriculture  
**Complexity**: Intermediate  
**Number of Ideas**: 5  

### Output:
- Project ideas with titles, descriptions, and detailed steps.
- Research papers and web results for deeper insights.

---

## Built With

- [Streamlit](https://streamlit.io/) - For the interactive UI
- [LangChain](https://langchain.com/) - To manage prompt templates and chains
- [Groq LLM](https://groq.com/) - For generating creative ideas
- [SerpAPI](https://serpapi.com/) - For fetching related web resources
- [Papers with Code](https://paperswithcode.com/) - For retrieving academic resources

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- Thanks to [LangChain](https://langchain.com/) and [Groq LLM](https://groq.com/) for their robust AI tools.
- Inspired by the curiosity of AI enthusiasts and builders worldwide.

---

Enjoy brainstorming with the **AI Project Idea Generator**! 🎉
