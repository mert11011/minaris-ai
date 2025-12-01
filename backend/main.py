from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# ---------------- LOAD ENV ----------------
backend_env = os.path.join(os.path.dirname(__file__), ".env")
root_env = os.path.join(os.path.dirname(__file__), "../.env")

if os.path.exists(backend_env):
    load_dotenv(backend_env)
elif os.path.exists(root_env):
    load_dotenv(root_env)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ---------------- FASTAPI APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- KNOWLEDGE BASE DISABLED ----------------
embeddings = None
texts = None
print("⚠️ Knowledge base disabled — starting lightweight backend for Render deploy.")

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are an intelligent GPT-5 assistant with access to Minaris triage domain knowledge.
However, the structured Excel knowledge base is currently unavailable.

Rules:
1. Answer using general reasoning only.
2. If the question references GMP, LIMA, Iovance, or triage:
   reply: "Excel knowledge base is temporarily unavailable — providing general reasoning:"
3. Be concise and accurate.
"""

class Message(BaseModel):
    message: str

# ---------------- MAIN ENDPOINT ----------------
@app.post("/analyze")
async def analyze(msg: Message):
    print(f"\n📩 Received: {msg.message}")

    prompt = (
        "Excel knowledge base is temporarily unavailable.\n\n"
        f"User question:\n{msg.message}\n\n"
        "Provide general reasoning-based guidance."
    )

    reply = ""

    # Tier 1: Reasoning model
    try:
        response = client.responses.create(
            model="gpt-5",
            reasoning={"effort": "low"},   # <-- lighter load
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=700,
        )
        reply = (response.output_text or "").strip()
    except Exception as e:
        print("❌ GPT-5 failed:", e)

    # Tier 2 fallback: smaller model
    if not reply:
        try:
            response = client.responses.create(
                model="gpt-5-instant",
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_output_tokens=700,
            )
            reply = (response.output_text or "").strip()
        except:
            reply = "⚠️ Backend error: Unable to generate response."

    return {"reply": reply}


@app.get("/")
def root():
    return {"status": "Backend running on Render (light mode)."}
