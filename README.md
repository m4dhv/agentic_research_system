# 📑ReportMind (Multi-Agent AI Research System)
<div align="center">

[![Streamlit App](https://img.shields.io/badge/Streamlit%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://reportmind.streamlit.app/)

<p> A Multi Agent AI Research System that supports writing detailed reports and asking related questions. <br> Built using LangChain with Gemini and the Tavily API. </p>
</div>
<details>
<summary>Table of Contents</summary>
  <ol>
    <li><a href="#core-features">Core Features</a></li>
    <li><a href="#screenshots--demo">Screenshots &amp; Deployment</a></li>
    <li><a href="#tech-stack">Tech Stack</a></li>
    <li><a href="#agent-architecture">Agent Architecture</a></li>
    <li><a href="#installation--setup">Installation &amp; Setup</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<a id="core-features"></a>
## ⭐ Core Features

- **Multi-Agent Pipeline**: Four specialised agents collaborate in a sequential pipeline to produce and review research reports.
- **BYOK Interface**: Interactive Streamlit UI which allows user to interact with the application through their own API Keys they can paste in the sidebar.
- **CLI Interface**: Command Line Interface for quick testing purposes.
- **Interactive Q&A**: Ask follow-up questions about any generated report via a persistent chat interface powered by an LCEL chain.
- **PDF & Markdown Export**: Download the final report as a formatted PDF (via ReportLab) or raw Markdown with one click.

<a id="screenshots--demo"></a>
## 🖼️ Screenshots & Deployment
Checkout the live deployment: **[reportmind.streamlit.app](https://reportmind.streamlit.app)**. <br> <br>
Streamlit UI:
<img width="960" height="510" alt="Processing screenshot" src="https://github.com/user-attachments/assets/247785ca-c9e0-4959-82e1-b7be7e307a69" /> <br><br>
<img width="960" height="510" alt="Screenshot 2026-09-04 144009" src="https://github.com/user-attachments/assets/480bc6d0-64a7-44ce-bd93-2d57a530b949" /> <br> <br>
<img width="960" height="510" alt="Screenshot 2026-09-04 144214" src="https://github.com/user-attachments/assets/c6391fec-ed8e-4dc1-9afd-4296679bbd5f" /> <br> <br>
CLI:
<img width="960" height="510" alt="Screenshot 2026-09-04 144531" src="https://github.com/user-attachments/assets/c6dacc12-4fbb-416d-ae21-41b8d657f299" />


<a id="tech-stack"></a>
## 🛠️ Tech Stack

- **Frontend and Hosting**: Streamlit with custom CSS
- **Agent Framework**: LangChain agents with LCEL chains and `ChatPromptTemplate`
- **Search**: Tavily Search API (`tavily-python`) with depth control
- **Web Scraping**: BeautifulSoup4, Requests, lxml
- **LLM**: Google Gemini (`gemini-3.5-flash-lite`) via `langchain-google-genai`
- **PDF Generation**: ReportLab (`reportlab`) with inline markdown rendering


<a id="agent-architecture"></a>
## 🤖 Agent Architecture

The pipeline runs four agents in sequence for every research request:

| Step | Agent | Role |
|------|-------|------|
| 1 | **Search Agent** | Queries Tavily and indexes top sources with titles, URLs, and key findings |
| 2 | **Reader Agent** | Selects the most authoritative URL and scrapes its full text with BeautifulSoup |
| 3 | **Writer Agent** | Synthesises both inputs into a structured report with numbered citations |
| 4 | **Critic Agent** | Reviews the report on depth, structure, and sourcing; returns a scored evaluation |

A fifth LCEL chain handles **Q&A**, answering follow-up questions grounded strictly in the generated report.

<a id="installation--setup"></a>
## ⚙️ Installation & Setup

1. **Clone & Install**:
   ```bash
   git clone https://github.com/m4dhv/agentic_research_system.git
   cd agentic_research_system
   pip install -r requirements.txt
   ```

2. **Configure**:
   Create a `.env` file and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   TAVILY_API_KEY=your_tavily_key_here
   ```

3. **Run**: <br>
   i) To run the streamlit interface:
   ```bash
   streamlit run app.py
   ```
   Go to: 
   ```bash
   http://localhost:8501/
   ```
   ii) To run the CLI:
   ```bash
   py pipeline.py
   ```
   ### API Keys
   - **Gemini API Key**: Obtain from [Google AI Studio](https://ai.google.dev/tutorials/setup)
   - **Tavily API Key**: Obtain from [Tavily](https://tavily.com/)

   Keys can also be entered directly in the sidebar at runtime and are never stored server-side.

<a id="project-structure"></a>
## 📁 Project Structure

```
agentic_research_system/
├── app.py          : Streamlit UI, Follow up questions, PDF generation
├── agents.py       : LLM init, Search Agent, Reader Agent, Writer chain, Critic chain
├── pipeline.py     : Pipeline orchestrator to run the backend correctly, CLI interface
├── tools.py        : Tavily search tool, URL scraper, source tracker
└── requirements.txt
```

<a id="acknowledgements"></a>
## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for hosting and frontend.
- [LangChain](https://www.langchain.com/) for the agent framework and LCEL chain abstractions.
- [Google Gemini](https://ai.google.dev/) for the underlying language model.
- [Tavily](https://tavily.com/) for the search API purpose-built for AI agents.
- [ReportLab](https://www.reportlab.com/) for PDF generation.
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for web scraping and HTML parsing.

<a id="license"></a>
## 📄 License
This project is licensed under the MIT License: [details](LICENSE).