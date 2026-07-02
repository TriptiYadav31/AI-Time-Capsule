import sys
import os
from google import genai

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "embeddings"))
from build_vector_db import search
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)


def build_prompt(question, month_prefix, chunks):
    context = "\n".join(f"- [{c['date']} | {c['source']}] {c['text']}" for c in chunks)
    return f"""You are a time capsule AI. You only know about the world up to {month_prefix}.
You must answer using ONLY the information below. Do not use any knowledge from
outside this list, and do not mention events after {month_prefix}.

INFORMATION FROM {month_prefix}:
{context}

QUESTION: {question}

Answer in a natural, conversational way, as if you are speaking from inside that time period.
If the information above doesn't actually answer the question, say so honestly instead of guessing.
"""


def build_free_prompt(question, chunks):
    context = "\n".join(f"- [{c['date']} | {c['source']}] {c['text']}" for c in chunks)
    return f"""You are a knowledgeable AI assistant with access to real news,
world events, and music chart data spanning 2015 to 2026.

Answer the question below using ONLY the information provided.
If the answer isn't in the information, say so honestly.
Always mention the date of the source when relevant.

INFORMATION:
{context}

QUESTION: {question}

Answer naturally and conversationally.
"""


def answer(question, month_prefix):
    chunks = search(question, month_prefix, top_k=8)
    if not chunks:
        return NO_DATA_MESSAGE, [], False  # text, sources, has_data

    prompt = build_prompt(question, month_prefix, chunks)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text, chunks, True


def answer_free(question):
    chunks = search_all(question, top_k=8)
    if not chunks:
        return NO_DATA_MESSAGE, [], False

    prompt = build_free_prompt(question, chunks)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text, chunks, True


def main():
    if len(sys.argv) != 3:
        print('Usage: python answer_question.py "your question" YYYY-MM')
        sys.exit(1)

    question, month_prefix = sys.argv[1], sys.argv[2]
    print(f"\nAsking the {month_prefix} time capsule: {question}\n")
    result, _, has_data = answer(question, month_prefix)
    print(result)


if __name__ == "__main__":
    main()
