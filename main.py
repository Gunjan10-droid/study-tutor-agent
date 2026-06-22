# main.py
# Entry point for the Multi-Agent Study Tutor App.

import os
import json
import asyncio
from dotenv import load_dotenv

# Import our agents
from tutor_agent import tutor_agent
from quiz_agent import quiz_generator_agent, quiz_evaluator_agent
from memory_agent import MemoryAgent

# Import ADK runners
from google.adk.runners import InMemoryRunner

# Load environment variables from .env file
load_dotenv()

def extract_text(events):
    """Helper to extract combined text response from agent run events."""
    text_parts = []
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text_parts.append(part.text)
    return "".join(text_parts)

def parse_json_safely(raw_text):
    """Safely cleans and parses JSON string from model response, handling markdown blocks."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    return json.loads(cleaned)

async def main():
    print("==========================================")
    print("      🏫 WELCOME TO THE STUDY TUTOR       ")
    print("==========================================")

    # 1. API Key Setup
    if not os.getenv("GEMINI_API_KEY"):
        print("\n🔑 Gemini API Key not found in environment or .env file.")
        api_key = input("Please enter your Gemini API Key (or press Enter to exit): ").strip()
        if not api_key:
            print("Exiting tutor. An API Key is required to run the agents.")
            return
        
        # Write to .env to persist it locally for future runs
        with open(".env", "w", encoding='utf-8') as env_file:
            env_file.write(f"GEMINI_API_KEY={api_key}\n")
        os.environ["GEMINI_API_KEY"] = api_key
        print("✅ Saved API key to .env file!")

    # 2. Instantiate Runners for each agent
    tutor_runner = InMemoryRunner(agent=tutor_agent)
    generator_runner = InMemoryRunner(agent=quiz_generator_agent)
    evaluator_runner = InMemoryRunner(agent=quiz_evaluator_agent)

    # 3. Load Progress
    memory = MemoryAgent()
    memory.print_summary()

    # 4. Main Loop
    while True:
        topic = input("\nWhat topic would you like to study today? (or type 'exit' to quit): ").strip()
        if not topic or topic.lower() == 'exit':
            print("\nThank you for studying! See you next time. 👋")
            break

        # --- STEP 1: EXPLAIN THE TOPIC ---
        print(f"\n🧠 [Tutor Agent] is preparing an explanation for '{topic}'...")
        try:
            tutor_events = await tutor_runner.run_debug(f"Explain this topic simply: {topic}")
            explanation = extract_text(tutor_events)
            print("\n------------------ EXPLANATION ------------------")
            print(explanation)
            print("-------------------------------------------------")
        except Exception as e:
            print(f"\n❌ Error getting explanation: {e}")
            continue

        # Wait for student to read the explanation
        input("\nPress Enter when you are ready to take a quick quiz on this topic! 📝")

        # --- STEP 2: GENERATE QUIZ ---
        print(f"\n🎯 [Quiz Agent] is generating questions about '{topic}'...")
        try:
            gen_events = await generator_runner.run_debug(f"Generate 3 questions about: {topic}")
            raw_gen_text = extract_text(gen_events)
            
            try:
                quiz_data = parse_json_safely(raw_gen_text)
                questions = [
                    quiz_data["question_1"],
                    quiz_data["question_2"],
                    quiz_data["question_3"]
                ]
            except Exception as json_err:
                print(f"❌ Failed to parse quiz questions as JSON: {json_err}")
                print(f"Raw output was:\n{raw_gen_text}")
                continue
        except Exception as e:
            print(f"\n❌ Error generating quiz: {e}")
            continue

        # --- STEP 3: CONDUCT THE QUIZ ---
        print("\nLet's start the quiz! 🌟")
        score = 0
        
        for idx, question in enumerate(questions, 1):
            print(f"\nQuestion {idx}: {question}")
            
            # Allow up to 2 attempts for each question to learn from hints!
            attempts = 2
            answered_correctly = False
            
            while attempts > 0:
                student_answer = input("Your answer: ").strip()
                if not student_answer:
                    print("Please enter an answer.")
                    continue
                
                print("Checking answer...")
                prompt = (
                    f"Question: '{question}'\n"
                    f"Student Answer: '{student_answer}'\n"
                    f"Evaluate this answer."
                )
                
                try:
                    eval_events = await evaluator_runner.run_debug(prompt)
                    raw_eval_text = extract_text(eval_events)
                    
                    try:
                        evaluation = parse_json_safely(raw_eval_text)
                        correct = evaluation.get("correct", False)
                        feedback = evaluation.get("feedback", "No feedback provided.")
                    except Exception as json_err:
                        print(f"Error parsing evaluator response: {json_err}")
                        print(f"Raw output was:\n{raw_eval_text}")
                        # Fallback parsing/handling
                        correct = "correct" in raw_eval_text.lower() and "incorrect" not in raw_eval_text.lower()
                        feedback = raw_eval_text
                    
                    print(f"\n💡 {feedback}")
                    
                    if correct:
                        score += 1
                        answered_correctly = True
                        break
                    else:
                        attempts -= 1
                        if attempts > 0:
                            print("Try again!")
                        else:
                            print("Let's move to the next question.")
                except Exception as e:
                    print(f"Error checking answer: {e}")
                    break
            
            if answered_correctly:
                print("🎉 Correct!")
            else:
                print("❌ Moving on.")

        # --- STEP 4: SAVE PROGRESS ---
        print(f"\n💾 [Memory Agent] is saving your quiz score of {score}/3 for '{topic}'...")
        memory.record_session(topic, score)
        
        # Print progress summary
        memory.print_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTutor session stopped. Goodbye!")
