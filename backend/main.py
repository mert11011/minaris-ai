import os
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------
# LOAD ENV
# --------------------------------------------------
backend_env = os.path.join(os.path.dirname(__file__), ".env")
root_env = os.path.join(os.path.dirname(__file__), "../.env")

if os.path.exists(backend_env):
    load_dotenv(backend_env)
elif os.path.exists(root_env):
    load_dotenv(root_env)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --------------------------------------------------
# FASTAPI + CORS
# --------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "gpt_knowledge_files")

EMBEDDINGS_PATH = os.path.join(KNOWLEDGE_DIR, "embeddings.npy")
TEXTS_PATH = os.path.join(KNOWLEDGE_DIR, "texts.npy")
TRIAGE_XLSX = os.path.join(KNOWLEDGE_DIR, "Triage_Data.xlsx")

try:
    embeddings = np.load(EMBEDDINGS_PATH)
    texts = np.load(TEXTS_PATH, allow_pickle=True)
    print("📚 Embeddings loaded.")
except Exception as e:
    print("❌ ERROR loading embeddings:", e)
    embeddings = None
    texts = None

try:
    triage_df = pd.read_excel(TRIAGE_XLSX)
    print("📄 Excel loaded.")
except Exception as e:
    print("❌ ERROR loading Excel:", e)
    triage_df = None

# --------------------------------------------------
# SEMANTIC SEARCH
# --------------------------------------------------
def semantic_search(query, top_k=5):
    if embeddings is None or texts is None:
        return []

    try:
        q_embed = client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        ).data[0].embedding
    except Exception as e:
        print("❌ Embedding API error:", e)
        return []

    q = np.array(q_embed)
    emb = np.array(embeddings)

    norms = np.linalg.norm(emb, axis=1) * np.linalg.norm(q)
    sim = np.dot(emb, q) / norms

    idx = np.argsort(sim)[::-1][:top_k]
    return [{"text": texts[i], "score": float(sim[i])} for i in idx]

# --------------------------------------------------
# TRIAGE LOGIC
# --------------------------------------------------
SYSTEM_PROMPT = """
You are the Minaris Triage Reasoning Engine.
Use GMP structure and triage reasoning.
"""

class Message(BaseModel):
    message: str

def classify_event(text):
    t = text.lower()
    if any(k in t for k in ["deviation", "out of spec", "oops"]):
        return "Deviation"
    if any(k in t for k in ["nce", "near miss", "almost"]):
        return "NCE"
    if any(k in t for k in ["comment", "note", "observation"]):
        return "Comment"
    return "Unknown"

# --------------------------------------------------
# ANALYZE ENDPOINT
# --------------------------------------------------
@app.post("/analyze")
async def analyze(msg: Message):

    print("📥 Incoming request:", msg.message)

    triage_type = classify_event(msg.message)
    matches = semantic_search(msg.message)

    if matches:
        summary_context = "\n".join(
            [f"- ({m['score']:.2f}) {m['text']}" for m in matches]
        )
    else:
        summary_context = "No KB matches found."

    prompt = f"""
Triage Category: {triage_type}

Context:
{summary_context}

User Input:
{msg.message}

Provide structured triage reasoning.
"""

    try:
        response = client.responses.create(
            model="gpt-5",
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=1500,
        )
        reply = (response.output_text or "").strip()
        print("🤖 GPT-5 reply succeeded.")
    except Exception as e:
        # 🔥 THIS PRINTS THE REAL ERROR IN RENDER LOGS
        print("❌ GPT-5 ERROR:", e)
        reply = None

    if not reply:
        reply = "⚠️ Backend error: Unable to generate response."

    return {
        "reply": reply,
        "triage_type": triage_type,
        "matches": matches,
    }

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "Backend running with full knowledge base."}
