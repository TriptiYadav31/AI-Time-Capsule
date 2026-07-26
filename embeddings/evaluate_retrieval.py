import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from pinecone_search import search

TEST_CASES = [
    ("what song is everyone listening to", "2020-03", "billboard"),
    ("what is the number one song", "2021-01", "billboard"),
    ("popular music this week", "2022-02", "billboard"),
    ("what is happening in the world", "2020-03", "wikipedia_current_events"),
    ("biggest news story right now", "2022-02", "nyt"),
    ("what are people talking about", "2023-11", "nyt"),
    ("coronavirus pandemic update", "2020-03", "nyt"),
    ("lockdown restrictions", "2020-04", "wikipedia_current_events"),
    ("vaccine rollout news", "2021-01", "nyt"),
    ("us election results", "2024-11", "nyt"),
    ("war in ukraine", "2022-02", "wikipedia_current_events"),
    ("what happened this month", "2023-11", "wikipedia_current_events"),
]


def evaluate(top_k=5):
    hit_rates = []
    reciprocal_ranks = []
    avg_scores = []

    for question, month, expected_source in TEST_CASES:
        results = search(question, month, top_k=top_k)

        if not results:
            hit_rates.append(0)
            reciprocal_ranks.append(0)
            avg_scores.append(0)
            print(f"❌ NO RESULTS | {month} | {question[:50]}")
            continue

        hit = any(expected_source in r["source"] for r in results)
        hit_rates.append(1 if hit else 0)

        rr = 0
        for i, r in enumerate(results):
            if expected_source in r["source"]:
                rr = 1 / (i + 1)
                break
        reciprocal_ranks.append(rr)

        scores = [1 - r["distance"] for r in results]
        avg_score = sum(scores) / len(scores)
        avg_scores.append(avg_score)

        status = "✅" if hit else "⚠️"
        print(f"{status} Hit={hit} | RR={rr:.2f} | Score={avg_score:.2f} | {month} | {question[:50]}")

    print(f"\nHit Rate:              {sum(hit_rates)/len(hit_rates)*100:.1f}%")
    print(f"Mean Reciprocal Rank:  {sum(reciprocal_ranks)/len(reciprocal_ranks):.3f}")
    print(f"Avg Relevance Score:   {sum(avg_scores)/len(avg_scores):.3f}")


if __name__ == "__main__":
    for k in [3, 5, 8]:
        print(f"\n{'='*60}")
        print(f"Testing top_k = {k}")
        print(f"{'='*60}")
        evaluate(top_k=k)
