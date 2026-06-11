from agent import agent_executor

def chat():
    print("🎬 Movie Recommendation Agent")
    print("Type 'quit' to exit\n")
    print("Example queries:")
    print("  - Recommend a horror movie from the 90s rated R")
    print("  - Find me a PG-13 sci-fi movie from the 2000s with good ratings")
    print("  - Show me action movies from 2020 available on Netflix in India\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Agent: {result['output']}\n")
            print("-" * 60)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    chat()