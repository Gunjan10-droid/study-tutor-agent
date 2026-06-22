# quiz_agent.py
# This file defines the Quiz Agents responsible for generating questions and evaluating student answers.

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

# Agent to generate 3 simple questions about a topic.
# Instructed to return exactly a JSON object with question_1, question_2, and question_3.
quiz_generator_agent = LlmAgent(
    name="QuizGenerator",
    model="gemini-2.5-flash",
    instruction=(
        "You are a friendly Study Tutor. Generate exactly 3 simple, clear, "
        "and beginner-friendly questions about the provided topic.\n"
        "Return the questions in JSON format with exactly these keys:\n"
        "{\n"
        "  \"question_1\": \"...\",\n"
        "  \"question_2\": \"...\",\n"
        "  \"question_3\": \"...\"\n"
        "}"
    )
)

# Agent to check and evaluate a student's answer.
# Instructed to return exactly a JSON object with correct and feedback keys.
quiz_evaluator_agent = LlmAgent(
    name="QuizEvaluator",
    model="gemini-2.5-flash",
    instruction=(
        "You are a supportive tutor checking a student's answer. "
        "Determine if their answer is correct. "
        "Return a JSON object with exactly these keys:\n"
        "{\n"
        "  \"correct\": true or false,\n"
        "  \"feedback\": \"Your encouraging feedback and hints go here. If incorrect, give a friendly hint without giving away the direct answer.\"\n"
        "}"
    )
)
