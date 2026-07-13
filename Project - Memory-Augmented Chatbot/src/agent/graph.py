from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from src.agent.tools import tools
from src.agent.memory import memory_manager

# main state for the agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# setup the google model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    # just call the llm with current msg history
    messages = state["messages"]
    
    # force the bot to remember things so it doesn't give generic ai disclaimers
    sys_prompt = SystemMessage(content="You are a helpful AI assistant with perfect memory. You MUST remember the user's personal details if they tell you. NEVER say 'I don't have memory' because your chat history is provided to you. Answer directly based on the chat history.")
    
    response = llm_with_tools.invoke([sys_prompt] + messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# building the graph here
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
# if the model wants a tool, go to tools
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# compile graph and pass memory checkpointer so it remembers stuff
app = workflow.compile(checkpointer=memory_manager.get_checkpointer())

def chat(user_input: str, thread_id: str = "default_user"):
    # setup config for tracking the user thread
    config = {"configurable": {"thread_id": thread_id}}
    
    input_message = HumanMessage(content=user_input)
    
    final_response = None
    # loop through the stream events
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        msg = event["messages"][-1]
        
        # sometimes gemini returns weird json blocks instead of string, gotta parse it manually
        if isinstance(msg.content, list):
            final_response = "".join(block.get("text", "") for block in msg.content if isinstance(block, dict) and "text" in block)
        else:
            final_response = msg.content
            
    return final_response

if __name__ == "__main__":
    print("Welcome to Memory-Augmented Chatbot! (Type 'quit' to exit)")
    while True:
        user_msg = input("You: ")
        if user_msg.lower() in ['quit', 'exit']:
            break
        response = chat(user_msg)
        print(f"Bot: {response}\n")
