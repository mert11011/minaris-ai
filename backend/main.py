from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
backend_env_path = os.path.join(os.path.dirname(__file__), ".env")
root_env_path = os.path.join(os.path.dirname(__file__), "../.env")

if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path)
    print(f"🔑 Loaded .env from backend directory: {backend_env_path}")
elif os.path.exists(root_env_path):
    load_dotenv(root_env_path)
    print(f"🔑 Loaded .env from project root: {root_env_path}")
else:
    print(f"⚠️ .env file not found at: {backend_env_path} or {root_env_path}")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY missing — please ensure it's set in the .env file.")
else:
    print("✅ OPENAI_API_KEY successfully loaded.")

# ---------------- CONFIG ----------------
app = FastAPI()
client = OpenAI(api_key=api_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOAD KNOWLEDGE BASE ----------------
BASE_DIR = os.path.dirname(__file__)
EMBED_PATH = os.path.join(BASE_DIR, "../gpt_knowledge_files/embeddings.npy")
TEXT_PATH = os.path.join(BASE_DIR, "../gpt_knowledge_files/texts.npy")

embeddings = None
texts = None

try:
    embeddings = np.load(EMBED_PATH)
    texts = np.load(TEXT_PATH, allow_pickle=True)
    print(f"✅ Loaded {len(texts)} triage records successfully.")
except Exception as e:
    print(f"❌ Error loading embeddings/texts: {e}")
    embeddings, texts = None, None


# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are an intelligent GPT-5 assistant with access to a specialized knowledge base of Minaris triage events.
You can answer any general question like ChatGPT, but when the question relates to GMP, triage events,
client programs (e.g., LIMA, Iovance), or quality documentation, prioritize information from the Excel knowledge base.

Rules:
1. If the answer is covered by the Excel data, ground your reasoning in that context.
2. If no relevant data exists, explicitly say:
   "This topic is not covered in the provided Excel knowledge base. Here’s a general reasoning-based answer:"
3. Be concise, factual, and clear.
4. Never invent historical data.
"""


# ---------------- REQUEST MODEL ----------------
class Message(BaseModel):
    message: str


# ---------------- UTILITY: FIND TOP SIMILAR ----------------
def find_top_similar(query_text, top_k=3):
    if embeddings is None:
        return []

    # embed user query
    q_emb = client.embeddings.create(
        model="text-embedding-3-large",
        input=query_text
    ).data[0].embedding

    # cosine similarities
    sims = cosine_similarity([q_emb], embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]

    # only include strong matches
    return [texts[i] for i in top_indices if sims[i] > 0.30]


# ---------------- MAIN ENDPOINT ----------------
@app.post("/analyze")
async def analyze(msg: Message):
    try:
        print(f"\n📩 Received: {msg.message}")

        # Retrieve relevant triage context
        top_docs = find_top_similar(msg.message)
        has_context = len(top_docs) > 0

        if has_context:
            print("📘 Excel context FOUND")
            context = "\n\n".join(top_docs)
            full_prompt = (
                f"Relevant Excel knowledge:\n{context}\n\n"
                f"User question:\n{msg.message}\n\n"
                f"Use Excel knowledge as your main reference."
            )
        else:
            print("⚠️ No Excel context — answering generally")
            full_prompt = (
                f"No relevant Excel knowledge found.\n\n"
                f"User question:\n{msg.message}\n\n"
                "Answer generally like ChatGPT."
            )

        # ---------------- ATTEMPT GPT-5 REASONING ----------------
        reply_text = ""
        chosen_model = "gpt-5"

        try:
            response = client.responses.create(
                model=chosen_model,
                reasoning={"effort": "high"},
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                max_output_tokens=2000,
            )
            reply_text = (response.output_text or "").strip()
        except Exception as e:
            print("❌ GPT-5 reasoning failed →", e)

        # ---------------- FALLBACK: GPT-5-INSTANT ----------------
        if not reply_text:
            chosen_model = "gpt-5-instant"
            print("➡️ Switching to GPT-5-Instant...")
            try:
                response = client.responses.create(
                    model=chosen_model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": full_prompt},
                    ],
                    max_output_tokens=1500,
                )
                reply_text = (response.output_text or "").strip()
            except Exception as e:
                print("❌ GPT-5-Instant failed →", e)

        # ---------------- FINAL FALLBACK: GPT-4 ----------------
        if not reply_text:
            chosen_model = "gpt-4-turbo"
            print("➡️ Final fallback: GPT-4-Turbo")
            res = client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                max_tokens=1400,
                temperature=0.3,
            )
            reply_text = res.choices[0].message.content.strip()

        # ---------------- ADD CONTEXT COLOR ----------------
        if has_context:
            reply_text = f"🔵 **Excel-based reasoning:**\n{reply_text}"
        else:
            reply_text = f"🔴 **General reasoning:**\n{reply_text}"

        print(f"✅ FINAL ({chosen_model}):\n", reply_text)
        return {"reply": reply_text}

    except Exception as e:
        print("❌ Fatal backend error:", e)
        return {"reply": f"⚠️ Backend error: {str(e)}"}
