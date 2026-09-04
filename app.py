import streamlit as st
import os   
import io
import re
from dotenv import load_dotenv
from pipeline import run_research_pipeline
import agents

from langchain_core.prompts import ChatPromptTemplate #for question/answer
from langchain_core.output_parsers import StrOutputParser

from reportlab.lib.pagesizes import letter #pdf generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT

load_dotenv() #for runnning locally


def _inline_markdown_to_html(text: str) -> str:
    """Convert a small subset of inline markdown (bold/italic) to reportlab-safe markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", text)
    return text


def generate_report_pdf(report_markdown: str, topic: str) -> bytes:
    """Render a markdown-ish research report into a downloadable PDF (in-memory)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportBody", parent=styles["Normal"], fontSize=10.5, leading=15, spaceAfter=8, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="ReportH1", parent=styles["Heading1"], fontSize=18, spaceBefore=14, spaceAfter=10))
    styles.add(ParagraphStyle(name="ReportH2", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=8))
    styles.add(ParagraphStyle(name="ReportH3", parent=styles["Heading3"], fontSize=12, spaceBefore=10, spaceAfter=6))

    story = []
    bullet_buffer = []

    def flush_bullets():
        if bullet_buffer:
            story.append(ListFlowable(
                [ListItem(Paragraph(_inline_markdown_to_html(b), styles["ReportBody"])) for b in bullet_buffer],
                bulletType="bullet", leftIndent=18))
            bullet_buffer.clear()

    heading_map = {"### ": (4, "ReportH3"), "## ": (3, "ReportH2"), "# ": (2, "ReportH1")}

    for raw_line in (report_markdown or "").splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_bullets(); story.append(Spacer(1, 6)); continue
        matched = next(((prefix, style) for prefix, (_, style) in heading_map.items() if line.startswith(prefix)), None)
        if matched:
            flush_bullets()
            prefix, style = matched
            story.append(Paragraph(_inline_markdown_to_html(line[len(prefix):]), styles[style]))
        elif line.strip().startswith(("- ", "* ")):
            bullet_buffer.append(line.strip()[2:])
        else:
            flush_bullets()
            story.append(Paragraph(_inline_markdown_to_html(line), styles["ReportBody"]))

    flush_bullets()
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# Page Config
st.set_page_config(
    page_title = "ReportMind",
    page_icon = "📑",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

# Custom CSS for Gradient Theme and CSS Typewriter Animation
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

h1,h2,h3,h4,h5,h6{font-family:'Plus Jakarta Sans',sans-serif!important;letter-spacing:-.02em}
.main-header{text-align:center;margin-top:-1.5rem;margin-bottom:1rem}
.main-title{font-size:2.8rem;font-weight:800!important;color:#B63048!important;margin-bottom:0}
.sub-title{font-size:1.1rem;opacity:.8;font-weight:600;margin:2px 0 1rem}

div.stButton>button[kind="primary"],div.stDownloadButton>button[kind="primary"]{
    background:#B63048!important;border:none!important;color:#fff!important;font-weight:600;
}
div.stButton>button[kind="primary"]:hover,div.stDownloadButton>button[kind="primary"]:hover{
    box-shadow:0 4px 15px rgba(178, 142, 170,.35);transform:translateY(-1px)
}
button[data-baseweb="tab"]{font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600}
button[aria-selected="true"]{color:#B63048!important;border-bottom-color:#B63048!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 class="main-title">📑ReportMind</h1>
    <p class="sub-title">A Multi Agent AI Research System <br> Search → Write → Ask</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Write a research report on...")
#Sidebar for Configuring API Keys
env_gemini_key = os.getenv("GEMINI_API_KEY", "")
env_tavily_key = os.getenv("TAVILY_API_KEY", "")

with st.sidebar:
    st.title("Configurations")
    depth = st.selectbox("Select Research Depth", options=["quick", "standard", "deep"])
    st.text("Paste your API Keys: ")

    gemini_api_key = st.text_input("Gemini API Key", value=env_gemini_key, type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password", value=env_tavily_key)

    if not gemini_api_key or not tavily_api_key:
        st.error("Both API keys are required to perform research!")
    else:
        st.success("API keys are configured and ready to use.")
    st.divider()
    st.caption("Keys are not stored on the cloud.  \n To acquire keys, visit:   \n [Google AI Studio](https://ai.google.dev/tutorials/setup), [Tavily](https://tavily.com/)")

topic_col, button_col = st.columns([5, 1])
with topic_col:
    topic = st.text_input(label="Research topic", placeholder="...research topic", label_visibility="collapsed")
with button_col:
    start_research = st.button("Start Research", use_container_width=True, type="primary")

#Session state management
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# LIVE AGENT STATUS
if start_research:
    if not topic.strip():
        st.error("Please enter a research topic to begin.")
    elif not gemini_api_key.strip() or not tavily_api_key.strip():
        st.error("Please provide valid Gemini and Tavily API keys in the sidebar.")
    else:
        with st.status("Your report is being processed...", expanded=True) as status:
            try:
                from agents import build_search_agent, build_reader_agent, init_llm
                from tools import init_tavily, get_sources

                init_llm(gemini_api_key.strip())
                init_tavily(tavily_api_key.strip(), depth=depth)
                state = {}

                # 1. Search & Indexing
                status.write("**Step 1:** Searching the web & indexing sources...")
                search_res = build_search_agent().invoke({
                    "messages": [("user", f"find relevant information about: {topic.strip()}")]
                })
                state["search_results"] = search_res["messages"][-1].content
                state["sources"] = get_sources()
                
                # 2. Deep Reading & Extraction
                status.write("**Step 2:** Reading sources and extracting data...")
                reader_res = build_reader_agent().invoke({
                    "messages": [(
                        "user",
                        f"Based on search results about '{topic.strip()}', pick the most relevant URL and scrape it for deeper reading.\n"
                        f"Search results:\n{state['search_results'][:800]}"
                    )]
                })
                state["scraped_content"] = reader_res["messages"][-1].content

                # 3. Report Synthesis
                status.write("**Step 3:** Writer agent is writing the report...")
                research_combined = (
                    f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
                )
                state["report"] = agents.writer_chain.invoke({
                    "topic": topic.strip(),
                    "research": research_combined,
                })
                status.write("**Step 4:** Adding citations and formatting the report...")

                # 4. Peer Review Audit
                status.write("**Step 5:** Evaluating all aspects of report quality...")
                state["feedback"] = agents.critic_chain.invoke({"report": state["report"]})

                # Complete
                status.update(label="Research Report created successfully!", state="complete", expanded=False)

                st.session_state["research_result"] = state
                st.session_state["research_topic"] = topic.strip()
                st.session_state.messages = []

            except Exception as e:
                status.update(label="Pipeline Failed", state="error", expanded=True)
                st.error(f"Error during research: {str(e)}")

if "research_result" in st.session_state:
    # Extract values from the dictionary
    result = st.session_state.research_result
    report = result.get("report", "")
    sources = result.get("sources", [])
    feedback = result.get("feedback", "")
    search_results = result.get("search_results", "")
    scraped_content = result.get("scraped_content", "")
           
#Q&A Chat Section
qa_expanded = len(st.session_state.messages) > 0

with st.expander("💬 Ask a follow up question", expanded=qa_expanded):
    if "research_result" not in st.session_state:
        st.warning("📚 Generate a research report to ask questions about it.")
    else:
        st.divider()
        # Display previous chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user question input
        if user_query := st.chat_input("Ask a question about this research..."):
            with st.chat_message("user"):
                st.markdown(user_query)

            # Process answer using LangChain
            with st.chat_message("assistant"):
                if not report:
                    st.warning("Please generate a research report first.")
                else:
                    with st.spinner("Thinking..."):
                        # Initialize LLM and Prompt Template
                        agents.init_llm(gemini_api_key)
                        llm = agents.llm

                        prompt = ChatPromptTemplate.from_template(
                            "You are a helpful research assistant. Answer the user's "
                            "question using ONLY the provided research report.\n\n"
                            "Research Report:\n{report}\n\n"
                            "Question: {question}\n\n"
                            "Answer:"
                        )

                        # Construct LCEL Chain
                        chain = prompt | llm | StrOutputParser()

                        # Generate response
                        response = chain.invoke({"report": report, "question": user_query})
                        st.markdown(response)

                        st.session_state.messages.append({"role": "user", "content": user_query})
                        st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

#Tabs for report viewing
if "research_result" in st.session_state:
    report_tab, sources_tab, critic_tab, tab_raw = st.tabs(["Report", "Sources", "Critic", "Raw Data"])
    
    with report_tab:
        header_col, pdf_col, md_col = st.columns([4, 1, 1])
        if report:
            topic_slug = st.session_state.get("research_topic", "report").strip().replace(" ", "_") or "report"
            with pdf_col:
                st.download_button(
                    label="Download PDF",
                    type="primary",
                    data=generate_report_pdf(report, st.session_state.get("research_topic", "Research Report")),
                    file_name=f"{topic_slug}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with md_col:
                st.download_button(
                    label="Download MD",
                    type="primary",
                    data=report.encode("utf-8"),
                    file_name=f"{topic_slug}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        st.markdown(report if report else "Report not generated.")

    with sources_tab:
        if sources:
            st.markdown("### Sources Used in Research:")
            for i, src in enumerate(sources, start=1):
                st.markdown(f"**[{i}] {src.get('title', 'Source')}** - {src.get('url', '')}")
        else:
            st.markdown("No sources were found during the research process.")

    with critic_tab:
        if feedback:
            st.markdown("### Critique of the Research Report:")
            st.markdown(feedback)
        else:
            st.markdown("No critique was generated for the research report.")

    with tab_raw:
        st.subheader("Raw Data used")
        with st.expander("Search Results", expanded=True):
            if search_results:
                st.text_area(label="Search Results Output", value=search_results,
                             height=280, disabled=True, label_visibility="collapsed")
            else:
                st.info("No raw search results available.")

        with st.expander("Scraped Primary Document Content", expanded=False):
            if scraped_content:
                st.text_area(label="Scraped Content Output", value=scraped_content,
                             height=280, disabled=True, label_visibility="collapsed")
            else:
                st.info("No raw scraped contents available.")
