import os
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------
# LOAD ENV
# --------------------------------------------
backend_env = os.path.join(os.path.dirname(__file__), ".env")
root_env = os.path.join(os.path.dirname(__file__), "../.env")

if os.path.exists(backend_env):
    load_dotenv(backend_env)
elif os.path.exists(root_env):
    load_dotenv(root_env)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --------------------------------------------
# FASTAPI SETUP
# --------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "gpt_knowledge_files")

EMBEDDINGS_PATH = os.path.join(KNOWLEDGE_DIR, "embeddings.npy")
TEXTS_PATH = os.path.join(KNOWLEDGE_DIR, "texts.npy")
TRIAGE_XLSX = os.path.join(KNOWLEDGE_DIR, "Triage_Data.xlsx")

embeddings = None
texts = None
triage_df = None

try:
    embeddings = np.load(EMBEDDINGS_PATH)
    texts = np.load(TEXTS_PATH, allow_pickle=True)
    print("📚 Embeddings loaded successfully.")
except Exception as e:
    print("⚠️ Failed to load embeddings:", e)

try:
    triage_df = pd.read_excel(TRIAGE_XLSX)
    print("📄 Triage Excel loaded.")
except Exception as e:
    print("⚠️ Failed to load triage Excel:", e)

# --------------------------------------------
# MATCHING FUNCTION
# --------------------------------------------
def semantic_search(query, top_k=5):
    if embeddings is None or texts is None:
        return []

    # Get query embedding using GPT-5’s embedding API
    q_embed = client.embeddings.create(
        model="text-embedding-3-large",
        input=query
    ).data[0].embedding

    q = np.array(q_embed)
    emb = np.array(embeddings)

    # cosine similarity
    norms = np.linalg.norm(emb, axis=1) * np.linalg.norm(q)
    sim = np.dot(emb, q) / norms

    # top matches
    idx = np.argsort(sim)[::-1][:top_k]

    results = []
    for i in idx:
        results.append({
            "text": texts[i],
            "score": float(sim[i])
        })

    return results

# --------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------
SYSTEM_PROMPT = """
You are the Minaris Triage Reasoning Engine.

You have access to:
- Semantic knowledge base (Excel-derived)
- Triage domain rules (Deviation / NCE / Comment)

Rules:
1. If a question references GMP, QC, QA, EM, LIMA, Iovance, CAR-T, TIL, or triage events:
   Respond using knowledge base + general reasoning.
2. If embeddings are missing, say:
   "Knowledge base unavailable — switching to general reasoning."
3. ALWAYS return clear triage-style structured answers.
"""

# --------------------------------------------
# REQUEST BODY MODEL
# --------------------------------------------
class Message(BaseModel):
    message: str

# --------------------------------------------
# TRIAGE LOGIC
# --------------------------------------------
def classify_event(user_text):
    event_text = user_text.lower()
    if any(k in event_text for k in ["deviation", "out of spec", "oops"]):
        return "Deviation"
    if any(k in event_text for k in ["nce", "near miss", "almost"]):
        return "NCE"
    if any(k in event_text for k in ["comment", "note", "observation"]):
        return "Comment"
    return "Unknown"

# --------------------------------------------
# MAIN ANALYZE ENDPOINT
# --------------------------------------------
@app.post("/analyze")
async def analyze(msg: Message):
    print(f"\n📩 Received: {msg.message}")

    triage_type = classify_event(msg.message)
    matches = semantic_search(msg.message)

    summary_context = "\n".join(
        [f"- ({m['score']:.2f}) {m['text']}" for m in matches]
    ) if matches else "No KB matches found."

    prompt = f"""
Triage category: {triage_type}

Relevant knowledge base matches:
{summary_context}

User message:
{msg.message}

Provide a structured triage-style response.
"""

    reply = ""

    try:
        # reasoning-capable model
        response = client.responses.create(
            model="gpt-5",
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_output_tokens=2000,
        )
        reply = (response.output_text or "").strip()

    except Exception as e:
        print("❌ GPT-5 reasoning failed:", e)

    if not reply:
        try:
            response = client.responses.create(
                model="gpt-5-instant",
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_output_tokens=1200,
            )
            reply = (response.output_text or "").strip()
        except:
            reply = "⚠️ Backend error: Unable to generate response."

    return {
        "reply": reply,
        "triage_type": triage_type,
        "matches": matches
    }

# --------------------------------------------
# HEALTH CHECK
# --------------------------------------------
@app.get("/")
def root():
    return {"status": "Backend running with full knowledge base."}
