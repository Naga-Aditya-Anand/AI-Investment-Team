import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import asyncio
from curl_cffi import requests
import yfinance as yf
from graphs.team_graph import team_graph
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Investment Team")

session = requests.Session(impersonate='chrome')

class AgentRequest(BaseModel):
    ticker: str
    query: str

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5173",           # Allows requests from specified origins
    allow_credentials=True,         # Allows cookies and authentication headers
    allow_methods=["*"],             # Allows all standard HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allows all HTTP headers
)

@app.get("/price")
async def current_price(ticker: str):
    try:
        stock = yf.Ticker(ticker,session=session)
        info = stock.info

        price = info['regularMarketPrice']
        prev_close = info['regularMarketPreviousClose']
        change = price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't fetch price for {ticker}: {e}")

@app.post("/stream")
async def stream_agent(request: AgentRequest):
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    initial_state = {
        "ticker": request.ticker.upper(),
        "query": request.query,
        "votes": [],
        "messages": [],
        "final_decision": "",
        "final_reasoning": "",
        "final_price_target": None,
        "team_summary": "",
    }

    async def event_generator():

        async for event in team_graph.astream_events(input=initial_state,config=config):

            kind = event["event"]

            # with open("logs.txt",'a') as file:
            #     print(event,file=file)

            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                tokens = event["data"]["chunk"].usage_metadata
                if content:
                    yield f"data: {json.dumps({'type':'token','node':event['metadata']['langgraph_checkpoint_ns'].split(':')[0],'content':content[0]['text'],'inputTokens':tokens['input_tokens'],'outputTokens':tokens['output_tokens'],'totalTokens':tokens['total_tokens']})}\n\n"
                elif tokens:
                    yield f"data: {json.dumps({'type':'usage','node':event['metadata']['langgraph_checkpoint_ns'].split(':')[0],'inputTokens':tokens['input_tokens'],'outputTokens':tokens['output_tokens'],'totalTokens':tokens['total_tokens']})}\n\n"

        
    return StreamingResponse(event_generator(),media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True) 