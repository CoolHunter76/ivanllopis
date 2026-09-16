import json
from pathlib import Path
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
BASE=Path(__file__).resolve().parent
SUPPORTED=("es","ca","eu","en","fr","uk","it","tr")
app=FastAPI(title="IvanLlopis.net",version="1.7.0")
app.mount("/static",StaticFiles(directory=BASE/"static"),name="static")
templates=Jinja2Templates(directory=BASE/"templates")
def trn(l):return json.loads((BASE/"translations"/f"{l if l in SUPPORTED else 'es'}.json").read_text(encoding="utf-8"))
def ctx(l,**x):return {"lang":l,"t":trn(l),"language_data":{c:trn(c) for c in SUPPORTED},**x}
TECH=[("microsoft.svg","Microsoft"),("dotnet.svg",".NET / C#"),("azure.svg","Azure"),("copilot.svg","Copilot"),("python.svg","Python"),("fastapi.svg","FastAPI"),("sql.svg","SQL Server"),("postgresql.svg","PostgreSQL"),("mongodb.svg","MongoDB"),("docker.svg","Docker")]
AI=[("copilot.svg","Microsoft Copilot"),("chatgpt.svg","OpenAI ChatGPT"),("claude.svg","Claude"),("gemini.svg","Google Gemini"),("mistral.svg","Mistral AI"),("llama.svg","Meta Llama"),("perplexity.svg","Perplexity") ]
HOBBIES=[("🏊","Swimming"),("🥾","Trekking"),("🎮","Gaming"),("🥁","Drums"),("✈️","Travel"),("💃","Latin Dance")]
@app.get("/health",include_in_schema=False)
def health():return {"status":"ok","languages":SUPPORTED}
@app.get("/",include_in_schema=False)
def root():return RedirectResponse("/es",307)
@app.get("/{lang}",response_class=HTMLResponse,include_in_schema=False)
def home(request:Request,lang:str):
 if lang not in SUPPORTED:return RedirectResponse("/es",307)
 return templates.TemplateResponse(request=request,name="home.html",context=ctx(lang,technologies=TECH,ai_engines=AI))
@app.get("/{lang}/hobbies",response_class=HTMLResponse,include_in_schema=False)
def hobbies(request:Request,lang:str):
 if lang not in SUPPORTED:return RedirectResponse("/es/hobbies",307)
 return templates.TemplateResponse(request=request,name="hobbies.html",context=ctx(lang,hobbies=HOBBIES))
