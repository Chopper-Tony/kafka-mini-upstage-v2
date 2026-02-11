import os
import argparse
import json
from agent.graph import build_graph
from agent.utils import extract_youtube_video_id, get_youtube_transcript


def pretty_print(result: dict):
    print(f"\n========== CONTENT TYPE: {result.get('content_type', 'N/A')} ==========")
    
    print("\n========== SUMMARY ==========")
    try:
        s = json.loads(result.get("summary", "{}"))
        print(s.get("Summary", s))
    except Exception:
        print(result.get("summary", ""))

    print("\n========== QUIZ ==========")
    try:
        q = json.loads(result.get("quiz", "{}"))
        questions = q.get("questions", [])
        if not questions:
            print("(no quiz items)")
        for i, item in enumerate(questions, 1):
            print(f"\nQ{i}. {item.get('text') or item.get('question')}")
            for j, opt in enumerate(item.get("options", []), 1):
                print(f"  {j}) {opt}")
            print("  정답:", item.get("answer"))
    except Exception:
        print(result.get("quiz", ""))

    print("\n========== JUDGE ==========")
    print("score:", result.get("judge_score"))
    print("needs_improve:", result.get("needs_improve"))
    print("improve_count:", result.get("improve_count", 0))

    print("\n========== RAG ==========")
    print("query:", result.get("query", ""))
    cits = result.get("citations", [])
    if cits:
        print("citations:")
        for c in cits:
            print(f" - {c.get('id')}")
    else:
        print("citations: (none)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, help="Input text")
    parser.add_argument("--url", type=str, help="YouTube video URL")
    args = parser.parse_args()

    input_text = ""
    if args.url:
        try:
            video_id = extract_youtube_video_id(args.url)
            input_text = get_youtube_transcript(video_id)
            print(f"YouTube transcript extracted (Length: {len(input_text)})")
        except Exception as e:
            print(f"Error extracting YouTube transcript: {e}")
            return
    elif args.text:
        input_text = args.text
    else:
        raise ValueError('No input. Try: python main.py --url "https://youtu.be/..." or --text "..."')

    if not os.getenv("UPSTAGE_API_KEY"):
        raise ValueError("UPSTAGE_API_KEY not set")

    graph = build_graph()
    result = graph.invoke({"input_text": input_text, "max_improve": 2})
    pretty_print(result)


if __name__ == "__main__":
    main()
