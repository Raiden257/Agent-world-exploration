# LLM Agent in a Virtual World

## Setup
1. Clone the repo
2. Install dependencies: pip install -r requirements.txt
3. Copy .env.example to .env and add your Groq API key
   - Get a free key at console.groq.com

## Running
python main.py

## Tasks
Two tasks are available in tasks.py — change the task_name
variable in main.py to switch between them:
- "simple_navigation"    — navigate to the goal
- "find_key_and_open_door" — find the key, unlock the door, reach goal

## Controls
The agent runs autonomously. Watch the terminal for step-by-step output.