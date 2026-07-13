from langchain.agents.middleware import AgentMiddleware
from langchain.messages import SystemMessage

class ToolCallLimitMiddleware(AgentMiddleware):
    
    def __init__(self,max_tool_calls):
        self.max_tool_calls = max_tool_calls

    def tool_call_count(self,state) -> int:
        return sum(
            len(getattr(m, "tool_calls", []) or [])
            for m in state["messages"]
        )
    
    def wrap_model_call(self, request, handler):
        state = request.state
        if self.tool_call_count(state) >= self.max_tool_calls:
            request = request.override(tools=[],tool_choice="none")
        return handler(request)
    
    def after_model(self, state, runtime):
        if self.tool_call_count(state) >= self.max_tool_calls:
            return {"messages": [
            SystemMessage(content="Tool limit reached — answer now using only the data already gathered.")
            ]}