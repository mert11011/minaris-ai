import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# --- Load environment variable (.env detection anywhere) ---
env_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY environment variable not found.")
else:
    print("🔑 OPENAI_API_KEY successfully loaded.")

# --- Initialize OpenAI client ---
client = OpenAI(api_key=api_key)

# --- Paths ---
excel_path = os.path.join(os.path.dirname(__file__), "../GPT knowledge files/Triage_Data.xlsx")
emb_path   = os.path.join(os.path.dirname(__file__), "../GPT knowledge files/embeddings.npy")
text_path  = os.path.join(os.path.dirname(__file__), "../GPT knowledge files/texts.npy")

# --- Load Excel ---
print(f"📘 Loading Excel file: {excel_path}")
df = pd.read_excel(excel_path).fillna("")
print("📊 Columns found:", df.columns.tolist())

# --- Prepare combined text records for embedding ---
records = []
for _, row in df.iterrows():
    title   = str(row.get("Title", "")).strip()
    what    = str(row.get("What Occurred?", "")).strip()
    client_ = str(row.get("Client Name", "")).strip()
    inv     = str(row.get("Investigation Number", "")).strip()
    risk    = str(row.get("Risk Level", "")).strip()
    status  = str(row.get("Status of Request", "")).strip()

    if not any([title, what, client_]):
        continue

    combined = (
        f"Title: {title} | What Occurred: {what} | Client: {client_} | "
        f"Investigation: {inv} | Risk: {risk} | Status: {status}"
    )
    records.append(combined)

print(f"✅ Prepared {len(records)} rows for embedding")

# --- Generate embeddings (version-safe call) ---
embeddings = []
for text in tqdm(records, desc="⚙️ Embedding rows"):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        # Works for SDK v2.0+ — explicit data access
        emb = response.data[0].embedding
        embeddings.append(emb)
    except Exception as e:
        print(f"⚠️ Skipping row due to error: {e}")

# --- Save results ---
np.save(emb_path, np.array(embeddings))
np.save(text_path, np.array(records))

print(f"✅ Saved embeddings to {emb_path}")
print(f"✅ Saved text data to {text_path}")
print("🎯 Rebuild complete.")
