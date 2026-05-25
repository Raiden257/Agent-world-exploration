import os
from dotenv import load_dotenv
load_dotenv()

from world import World
from tasks import load_task
from agent import run_loop

import sys

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

    sys.stdout = Logger("run_log.txt")


def main():
    print("╔══════════════════════════════╗")
    print("║   LLM Agent — Virtual World  ║")
    print("╚══════════════════════════════╝\n")

    # Choose which task to run
    task_name = "find_key_and_open_door"
    task = load_task(task_name)

    print(f"Task: {task['description']}\n")

    # Build the world from the task layout
    world = World(task["layout"])

    # Hand off to the agent loop
    success = run_loop(world, max_steps=60)

    # Final summary
    print("─" * 40)
    if success:
        print(f"✓ Completed in {world.steps_taken} steps")
    else:
        print(f"✗ Failed after {world.steps_taken} steps")

if __name__ == "__main__":
    
    main()