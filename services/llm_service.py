
import json
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen3:8b"


def generate_career_analysis(assessment):
    prompt = f"""
You are Career Pathfinder, a practical career guidance assistant.

Create a personalized career assessment and a realistic four-week learning plan.

USER PROFILE:
Education: {assessment.education}
Interest: {assessment.interest}
Python level (0-3): {assessment.python_level}
Math level (0-3): {assessment.math_level}
Coding level (0-3): {assessment.coding_level}
Daily available hours: {assessment.daily_hours}
Goal: {assessment.goal}

Return ONLY valid JSON. Do not use Markdown fences or text outside the JSON.

Use exactly this structure:
{{
  "career_direction": "Recommended career and why",
  "strengths": ["strength 1", "strength 2"],
  "skills_to_improve": ["skill 1", "skill 2"],
  "weeks": [
    {{
      "week": 1,
      "title": "Short week title",
      "goal": "What the user should achieve this week",
      "days": [
        {{
          "day": 1,
          "task": "Specific task for this day"
        }}
      ],
      "milestone": "A measurable result at the end of the week"
    }}
  ],
  "daily_schedule": [
    {{
      "time": "First study block",
      "activity": "What to do"
    }}
  ],
  "project": {{
    "title": "Beginner-friendly project name",
    "description": "What to build",
    "steps": ["step 1", "step 2", "step 3"]
  }},
  "start_today": ["task 1", "task 2", "task 3"]
}}

IMPORTANT RULES:
- Include exactly four week objects in "weeks", numbered 1, 2, 3, and 4.
- Include exactly seven day objects per week, numbered 1 to 7.
- Make the tasks specific to the user's career interest, current skills, and goal.
- Progress from foundations in Week 1 to practice in Week 2, a project in Week 3, and project completion and review in Week 4.
- Respect the user's available daily study hours.
- Keep each daily task concise and achievable.
- Keep the complete response concise.
- Use realistic recommendations. Never guarantee employment.
- Do not assume skills the user has not demonstrated.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "options": {
                "temperature": 0.3,
                "num_predict": 1800
            }
        },
        timeout=(10, 240)
    )

    response.raise_for_status()
    data = response.json()
    content = data["message"]["content"]

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Ollama returned invalid JSON. Please try the assessment again."
        ) from exc

    if not isinstance(result, dict) or not isinstance(result.get("weeks"), list):
        raise ValueError("Ollama returned an unexpected roadmap format.")

    if len(result["weeks"]) != 4:
        raise ValueError("The generated roadmap must contain four weeks.")

    return result
