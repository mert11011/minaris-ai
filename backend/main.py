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
embeddings_path = os.path.join(os.path.dirname(__file__), "../GPT knowledge files/embeddings.npy")
texts_path = os.path.join(os.path.dirname(__file__), "../GPT knowledge files/texts.npy")

try:
    embeddings = np.load(embeddings_path)
    texts = np.load(texts_path, allow_pickle=True)
    print(f"✅ Loaded {len(texts)} triage records successfully.")
except Exception as e:
    print(f"❌ Error loading embeddings: {e}")
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
   and then answer like ChatGPT.
3. Be concise, factual, and clear — balance reasoning + helpful tone.
4. Never invent or fabricate historical data.
"""

# ---------------- INPUT MODEL ----------------
class Message(BaseModel):
    message: str

# ---------------- UTILITY: FIND TOP CONTEXT ----------------
def find_top_similar(query_text, top_k=3):
    """Return most similar triage entries from embeddings."""
    if embeddings is None or len(embeddings) == 0:
        return []
    q_emb = client.embeddings.create(
        model="text-embedding-3-large",
        input=query_text
    ).data[0].embedding
    sims = cosine_similarity([q_emb], embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    top_texts = [texts[i] for i in top_indices if sims[i] > 0.3]
    return top_texts

# ---------------- MAIN ENDPOINT ----------------
@app.post("/analyze")
async def analyze(msg: Message):
    """
    Hybrid GPT-5 assistant:
    - Uses Excel knowledge base if relevant context found
    - Otherwise answers like standard ChatGPT
    """
    try:
        print(f"\n📩 Received message: {msg.message}")

        # Retrieve relevant context
        top_docs = find_top_similar(msg.message, top_k=3)
        context = "\n\n".join(top_docs) if top_docs else ""
        has_context = bool(top_docs)

        if has_context:
            print("📖 Found relevant Excel knowledge.")
        else:
            print("⚠️ No Excel context found — answering generally.")

        # Compose prompt
        if has_context:
            full_prompt = (
                f"Relevant Excel knowledge:\n{context}\n\n"
                f"User question:\n{msg.message}\n\n"
                f"Use Excel knowledge as your main reference."
            )
        else:
            full_prompt = (
                f"The user asked: {msg.message}\n\n"
                "No relevant Excel knowledge found — answer generally like ChatGPT."
            )

        # --- Try GPT-5 Reasoning ---
        model_used = "gpt-5"
        print("⚙️ Running GPT-5 Extended Reasoning...")
        try:
            response = client.responses.create(
                model=model_used,
                reasoning={"effort": "high"},
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                max_output_tokens=2000,
            )
            reply_text = response.output_text.strip() if response.output_text else ""
        except Exception as e:
            print("❌ GPT-5 reasoning error:", e)
            reply_text = ""

        # --- Fallback GPT-5-Instant ---
        if not reply_text:
            model_used = "gpt-5-instant"
            print("⚠️ Empty → switching to GPT-5-Instant...")
            try:
                response = client.responses.create(
                    model=model_used,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": full_prompt},
                    ],
                    max_output_tokens=1500,
                )
                reply_text = response.output_text.strip() if response.output_text else ""
            except Exception as e:
                print("❌ GPT-5-Instant error:", e)
                reply_text = ""

        # --- Final fallback GPT-4 ---
        if not reply_text:
            model_used = "gpt-4-turbo"
            print("⚠️ Retrying with GPT-4-Turbo fallback...")
            response = client.chat.completions.create(
                model=model_used,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            reply_text = response.choices[0].message.content.strip()

        if not reply_text:
            reply_text = "⚠️ No valid text received from any model."

        # --- Add visual indicator (red or blue circle) ---
        if has_context:
            reply_text = f"🔵 **Excel-based reasoning:**\n{reply_text}"
        else:
            reply_text = f"🔴 **General reasoning (outside Excel data):**\n{reply_text}"

        print(f"✅ Final Reply ({model_used}):\n", reply_text)
        return {"reply": reply_text}

    except Exception as e:
        print("❌ Fatal backend error:", e)
        return {"reply": f"⚠️ Backend error: {str(e)}"}
