import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from tools import search_movies, get_streaming_availability
from langchain_classic.agents import create_react_agent, AgentExecutor


load_dotenv()

# --- LLM Setup ---
# Using Groq's Llama-3.3-70B — best open model for tool-calling / ReAct agents
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

REACT_PROMPT = PromptTemplate.from_template("""You are a movie recommendation assistant that queries a live movie database.

TOOLS AVAILABLE:
{tools}

STRICT OUTPUT FORMAT:
Thought: <your reasoning>
Action: <one of [{tool_names}]>
Action Input: <JSON string>
Observation: <tool result>
... repeat ...
Thought: I now have enough to answer.
Final Answer: <friendly response>

RULES:
- After every Thought, IMMEDIATELY write Action: — no prose in between
- search_movies does NOT support certification filtering — skip it in Action Input
- If user asks for R / PG-13 / PG, mention it in Final Answer as a note instead
- Genre must be lowercase: "science fiction" not "Science Fiction"
- "90s" = year_from=1990, year_to=1999 | "2000s" = year_from=2000, year_to=2009
- If user gives a specific movie title, use search_movie_by_title
- Always show at least 3 movies in Final Answer

Begin.

Question: {input}
Thought:{agent_scratchpad}""")

# Also update the tools list to include the new tool
from tools import search_movies, search_movie_by_title, get_streaming_availability

tools = [search_movies, search_movie_by_title, get_streaming_availability]

# --- Agent ---
agent = create_react_agent(llm, tools, REACT_PROMPT)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,           # Shows the full ReAct loop in terminal
    max_iterations=6,
    handle_parsing_errors=True,
)