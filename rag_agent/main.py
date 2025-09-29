# rag_agent/main.py
from rag_agent.services.llm_agent import answer_query

if __name__ == "__main__":
    print("=== Mini RAG Agent ===")
    print("Type a query (or 'exit' to quit):")

    while True:
        query = input("\nYour question: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Run query against summaries index
        result = answer_query(query, top_k=5, use_gemini=True)

        print("\n--- Retrieved Records ---")
        for i, r in enumerate(result["retrieved"], 1):
            md = r["metadata"].get("summary", {})
            print(
                f"[{i}] Patient: {md.get('Patient','')}, "
                f"Diagnosis: {md.get('Diagnosis','')}, "
                f"Treatment: {md.get('Treatment','')}, "
                f"Follow-up: {md.get('Follow-up','')} "
                f"(distance={r['distance']:.4f})"
            )

        if "answer" in result:
            print("\n--- Gemini Answer ---")
            print(result["answer"])
