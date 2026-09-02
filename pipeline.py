import agents
from agents import build_reader_agent, build_search_agent, init_llm
from tools import init_tavily, get_sources
from dotenv import load_dotenv
load_dotenv()
import shutil
w, _ = shutil.get_terminal_size()

def run_research_pipeline(
    topic: str,
    gemini_api_key: str | None = None,
    tavily_api_key: str | None = None,
    depth: str = "standard"
) -> dict:
    
    init_llm(gemini_api_key)
    init_tavily(tavily_api_key, depth=depth)
    
    state = {

    }

    
    #1: SEARCH AGENT WORKING
    print("\n" + "*"*w )
    print("step 1: search agent working")
    print("*" * w)
    
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"find relevant information about: {topic}")]
    })
    
    state["search_results"] = search_result["messages"][-1].content
    state["sources"] = get_sources()

    print("\n search result", state['search_results'])

    #2: reader agent working
    print("\n" + "*" * w)
    print("step 2: reader agent working")
    print("*" * w)

    
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
    "messages": [
        (
            "user",
            f"Based on search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper reading.\n"
            f"Search results:\n{state['search_results'][:800]}"
        )
    ]
})
    
    state['scraped_content'] = reader_result["messages"][-1].content
 
    print("\n scraped content", state['scraped_content'])   
    
    
    #3: writer chain working
    print("\n" + "*" * w)
    print("step 3: writer chain is drafting the report")
    print("*" * w)
    
    
    research_combined = (
        f"SEARCH RESULTS: \n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"   
    )
    
    state["report"] = agents.writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    
    print("\n final report\n", state['report'])
    
    #critic report
    print("\n" + "*" * w)
    print("step 4: critic chain is reviewing the report")
    print("*" * w)
    
    state["feedback"] = agents.critic_chain.invoke({
        "report":state['report']
    })
    #state["critic_report"] = state["feedback"]
    
    
    print("\n critic report\n", state['feedback'])
    
    
    return state
    
if __name__ == "__main__":
    topic  = input("\n Enter a research topic:")
    run_research_pipeline(topic)
        
        
    