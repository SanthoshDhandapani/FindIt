"""
Validates the full environment setup: .env keys, Docker services, Pinecone index,
Gemini API, and embedding model.

Usage: python scripts/validate_setup.py
"""

import sys
import os

from dotenv import load_dotenv

load_dotenv()

CHECKS_PASSED = 0
CHECKS_FAILED = 0


def check(name, fn):
    global CHECKS_PASSED, CHECKS_FAILED
    try:
        result = fn()
        print(f"  [PASS] {name}: {result}")
        CHECKS_PASSED += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        CHECKS_FAILED += 1


# --- 1. Environment variables ---
print("\n1. Environment variables")
required_keys = ["GEMINI_API_KEY", "PINECONE_API_KEY", "HF_TOKEN", "DATABASE_URL", "REDIS_URL"]
for key in required_keys:
    check(key, lambda k=key: f"{os.environ[k][:10]}..." if os.environ.get(k) else (_ for _ in ()).throw(KeyError(f"{k} not set")))

# --- 2. Redis ---
print("\n2. Redis")
def check_redis():
    import redis
    r = redis.from_url(os.environ["REDIS_URL"])
    r.ping()
    return "PONG"
check("Redis connection", check_redis)

# --- 3. PostgreSQL ---
print("\n3. PostgreSQL")
def check_postgres():
    import asyncio
    import asyncpg

    db_url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")

    async def test_conn():
        conn = await asyncpg.connect(db_url)
        val = await conn.fetchval("SELECT 1")
        await conn.close()
        return val

    val = asyncio.run(test_conn())
    return f"SELECT 1 = {val}"
check("PostgreSQL connection", check_postgres)

# --- 4. Gemini API ---
print("\n4. Gemini API")
def check_gemini():
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(model="gemini-2.5-flash", contents="Say OK")
    return resp.text.strip()[:50]
check("Gemini gemini-2.5-flash", check_gemini)

# --- 5. Pinecone ---
print("\n5. Pinecone")
def check_pinecone():
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    idx = pc.describe_index("ecommerce-search")
    return f"dim={idx.dimension}, metric={idx.metric}, state={idx.status['state']}"
check("Pinecone index (ecommerce-search)", check_pinecone)

# --- 6. Embedding model ---
print("\n6. Embedding model")
def check_embedding():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vec = model.encode("test")
    return f"{len(vec)} dims"
check("all-MiniLM-L6-v2", check_embedding)

# --- Summary ---
total = CHECKS_PASSED + CHECKS_FAILED
print(f"\n{'='*50}")
print(f"Results: {CHECKS_PASSED}/{total} passed, {CHECKS_FAILED}/{total} failed")
if CHECKS_FAILED > 0:
    print("Fix the failed checks above before proceeding.")
    sys.exit(1)
else:
    print("All checks passed. Environment is ready!")
    sys.exit(0)
