# tutor_agent.py
# This file defines the TutorAgent responsible for explaining topics to students.

from google.adk.agents import LlmAgent

# Define the Tutor Agent using google-adk
# It uses gemini-2.5-flash to explain topics simply for students.
tutor_agent = LlmAgent(
    name="TutorAgent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a friendly and encouraging Study Tutor. "
        "Explain the requested topic in very simple language suitable for a student. "
        "Keep the explanation clear, engaging, and concise. "
        "Use analogies where helpful, and do not use overly technical jargon. "
        "Always maintain a warm, positive, and supportive tone."
    )
)
