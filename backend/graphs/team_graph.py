from langgraph.graph import StateGraph,END,START
from langgraph.checkpoint.memory import MemorySaver

from agents.economist import economist_node
from agents.fundamental_analyst import fundamental_analyst_node
from agents.news_analyst import news_analyst_node
from agents.portfolio_manager import portfolio_manager_node
from agents.risk_manager import risk_manager_node
from agents.sentiment_analyst import sentiment_analyst_node
from agents.technical_analyst import technical_analyst_node
from graphs.state import TeamState

def build_team_graph():

    graph = StateGraph(TeamState)

    # Nodes
    graph.add_node(fundamental_analyst_node,"fundamental_analyst_node")
    graph.add_node(technical_analyst_node,"technical_analyst_node")
    graph.add_node(news_analyst_node,"news_analyst_node")
    graph.add_node(sentiment_analyst_node,"sentiment_analyst_node")
    graph.add_node(risk_manager_node,"risk_manager_node")
    graph.add_node(economist_node,"economist_node")
    graph.add_node(portfolio_manager_node,"portfolio_manager_node")

    # Edges
    graph.add_edge(START,"fundamental_analyst_node")
    graph.add_edge(START,"technical_analyst_node")
    graph.add_edge(START,"news_analyst_node")
    graph.add_edge(START,"sentiment_analyst_node")
    graph.add_edge(START,"risk_manager_node")
    graph.add_edge(START,"economist_node")

    graph.add_edge("fundamental_analyst_node","portfolio_manager_node")
    graph.add_edge("technical_analyst_node","portfolio_manager_node")
    graph.add_edge("news_analyst_node","portfolio_manager_node")
    graph.add_edge("sentiment_analyst_node","portfolio_manager_node")
    graph.add_edge("risk_manager_node","portfolio_manager_node")
    graph.add_edge("economist_node","portfolio_manager_node")

    graph.add_edge("portfolio_manager_node",END)

    memory = MemorySaver()

    return graph.compile(checkpointer=memory)

team_graph = build_team_graph()

from IPython.display import Image
png_data = team_graph.get_graph().draw_mermaid_png()
with open("graph_visualization.png", "wb") as f:
    f.write(png_data)
print("Graph saved to graph_visualization.png")