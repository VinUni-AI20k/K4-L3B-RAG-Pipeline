import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import generate_with_citation

query = "Toi co the tra hang trong bao nhieu ngay?"

print("=== SEMANTIC SEARCH ===")
try:
    dense = semantic_search(query, top_k=3)
    print(f"Dense count: {len(dense)}")
    for r in dense[:2]:
        print(f"  score={r['score']:.4f}  method={r['retrieval_method']}  id={r['id'][:50]}")
except Exception as e:
    print(f"DENSE ERROR: {e}")

print()
print("=== LEXICAL SEARCH ===")
try:
    sparse = lexical_search(query, top_k=3)
    print(f"BM25 count: {len(sparse)}")
    for r in sparse[:2]:
        print(f"  score={r['score']:.4f}  method={r['retrieval_method']}  id={r['id'][:50]}")
except Exception as e:
    print(f"BM25 ERROR: {e}")

print()
print("=== RETRIEVE PIPELINE ===")
try:
    results = retrieve(query, top_k=3)
    print(f"Retrieve count: {len(results)}")
    for r in results:
        print(f"  score={r['score']:.4f}  method={r['retrieval_method']}  id={r['id'][:50]}")
except Exception as e:
    print(f"RETRIEVE ERROR: {e}")

print()
print("=== GENERATION ===")
try:
    out = generate_with_citation(query, top_k=3)
    print(f"retrieval_source: {out['retrieval_source']}")
    print(f"sources count: {len(out['sources'])}")
    print(f"answer: {out['answer'][:300]}")
except Exception as e:
    import traceback
    print(f"GENERATION ERROR: {e}")
    traceback.print_exc()
