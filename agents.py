from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
import os
from dotenv import load_dotenv

load_dotenv()

#LLM Configuration
llm = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite")


#Search Agent Configuration
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search],
        system_prompt="""Act as an autonomous Lead Intelligence Researcher.

Your objective is to find high-signal, authoritative, and timely information regarding the user's research query.

Instructions:
1. Use the web_search tool to retrieve the top relevant sources.
2. Formulate focused queries that prioritize credible reporting, technical documentation, and primary analysis.
3. Organize the search output cleanly as:

[Index] Title: <title>
URL: <url>
Key Findings: <concise summary of critical facts/data points>

Ensure all source URLs and index numbers are accurately preserved.
""" )
    
#Reader Agent Configuration
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url],
        system_prompt="""You are a Deep Document Analyst.

You receive curated search results containing URLs and snippets.

Instructions:
1. Evaluate the search results and select the single most authoritative, content-rich URL for the topic.
2. Use the scrape_url tool to extract the complete page text.
3. Synthesize and present the scraped content clearly, highlighting core data, technical specifics, and contextual nuance.
4. If valid URLs exist in the provided search results, always proceed with scraping.
"""
    )


#Writer Chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Senior Research Synthesizer. You produce comprehensive, analytical executive reports with clean in-text citations [1], [2]."),
    ("human", """Synthesize a rigorous, detailed research report on the following subject:

Topic: {topic}

Gathered Intelligence:
{research}

Report Requirements:
1. Introduction: High-level overview of the current landscape.
2. In-Depth Analysis: Minimum of 3 detailed thematic sections exploring key developments, data, and perspectives. Use precise numbered in-text citations (e.g. [1], [2]) directly tied to the numbered search sources. Never use placeholder citations like '[Scraped Content]'.
3. Conclusion: Future implications, trends, or potential challenges.
4. References: List all cited sources corresponding directly to their citation numbers (e.g. [1] Title - URL).

Maintain an objective, analytical, and authoritative tone throughout.

""")
])




writer_chain = writer_prompt | llm | StrOutputParser()

#Critic Chain

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a constructive Senior Research Editor and Reviewer. Provide a balanced, fair, and actionable critique of the research dossier."),
    ("human", """Review the following research report honestly and constructively:

Report:
{report}

Evaluation Criteria:
- Depth & Coverage: Did the report thoroughly address the core topic?
- Structure & Readability: Is the information well-organized, clear, and engaging?
- Sourcing & Evidence: Are key claims supported with citations?

Provide a constructive review structured as:
- Overall Score: [X/10] (Score fairly: 7-9/10 for solid, well-structured reports with good insights; reserve lower scores only for incomplete or misleading content)
- Key Strengths: What was done well
- Constructive Feedback: 1-2 actionable suggestions to make it even better
- Final Verdict: A short, balanced closing summary
""")
])



critic_chain = critic_prompt | llm | StrOutputParser()


def init_llm(gemini_api_key: str | None = None):
    global llm, writer_chain, critic_chain
    key = gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API key required. Set GEMINI_API_KEY in .env or pass it explicitly.")
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=key,
    )
    writer_chain = writer_prompt | llm | StrOutputParser()
    critic_chain = critic_prompt | llm | StrOutputParser()
