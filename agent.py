import os, time
from dotenv import load_dotenv
load_dotenv()                    # ← add this line here
from collections import Counter
from groq import Groq
from renderer import render_terminal
from world import WALL

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_prompt(observation, history):
    # Loop detection
    loop_warning = ""
    if len(history) >= 4:
        last_actions = [h['action'] for h in history[-6:]]
        counts = Counter(last_actions)
        repeated = [a for a, n in counts.items() if n >= 3]
        if repeated:
            loop_warning = f"⚠ WARNING: {repeated} is not working — pick a completely different action.\n"

    # Recent history
    history_text = "None yet."
    if history:
        history_text = "\n".join(
            f"  {h['action']} → {h['result']}"
            for h in history[-5:]
        )

    # Look one step ahead and suggest the unblocked axis first
    def path_hint(ar, ac, tr, tc, grid):
        vert  = "move_south" if tr > ar else "move_north"
        horiz = "move_east"  if tc > ac else "move_west"

        # Guard against empty grid
        if not grid or not grid[0]:
            return vert, horiz, "move toward target"

        rows = len(grid)
        cols = len(grid[0])

        next_r   = ar + (1 if tr > ar else -1)
        next_c_h = ac + (1 if tc > ac else -1)

        # Guard against out of bounds before indexing
        vert_blocked  = grid[next_r][ac] == WALL if 0 <= next_r < rows and 0 <= ac < cols else True
        horiz_blocked = grid[ar][next_c_h] == WALL if 0 <= ar < rows and 0 <= next_c_h < cols else True

        if vert_blocked and not horiz_blocked:
            return horiz, vert, "vertical path is blocked — go horizontal first"
        elif horiz_blocked and not vert_blocked:
            return vert, horiz, "horizontal path is blocked — go vertical first"
        else:
            return vert, horiz, "move toward target"

    # Dynamic strategy based on current game state
    has_key  = 'key' in observation['inventory']
    key_pos  = observation.get('key_pos')
    door_pos = observation.get('door_pos')
    grid     = observation.get('grid', [])
    ar, ac   = observation['position']

    if not has_key and key_pos:
        kr, kc = key_pos
        first, second, reason = path_hint(ar, ac, kr, kc, grid)
        strategy = f"""CURRENT GOAL: Pick up the key at row {kr}, col {kc}.
You are at row {ar}, col {ac}.
Best move: {first} ({reason})
If that is blocked: try {second}
If both are blocked: move the opposite direction to get around the wall.
Walk onto the K tile to collect it automatically."""

    elif has_key and door_pos:
        dr, dc = door_pos
        first, second, reason = path_hint(ar, ac, dr, dc, grid)
        strategy = f"""CURRENT GOAL: You have the key! Walk INTO the door at row {dr}, col {dc}.
You are at row {ar}, col {ac}.
Best move: {first} ({reason})
If that is blocked: try {second}
If both are blocked: move the opposite direction to get around the wall."""

    else:
        goal_pos = observation.get('goal_pos')
        if goal_pos:
            gr, gc = goal_pos
            first, second, reason = path_hint(ar, ac, gr, gc, grid)
            strategy = f"""CURRENT GOAL: Door is open — reach the goal G at row {gr}, col {gc}.
You are at row {ar}, col {ac}.
Best move: {first} ({reason})
If that is blocked: try {second}"""
        else:
            strategy = "CURRENT GOAL: Navigate to G."

    prompt = f"""You are navigating a grid. One word reply only.
@ = you, G = goal, W = wall, . = floor, K = key, D = door

{observation['text']}

RECENT ACTIONS:
{history_text}
{loop_warning}
{strategy}

RULES:
- If a move is blocked by a wall, try the other direction immediately
- Do not repeat the same failed action more than once
- You cannot move through walls — find a way around them

VALID ACTIONS: move_north move_south move_east move_west pick_up use_key
One word only. No explanation. No punctuation.

Action:"""

    return prompt


def get_action(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a navigation agent. Reply with a single action word only. No explanation, no punctuation, no extra text."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=5,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def parse_action(raw_text):
    """
    Cleans up the LLM's response. The model might say
    "I'll move north" instead of "move_north" — this fixes that.
    """
    valid_actions = [
        "move_north", "move_south", "move_east", "move_west",
        "pick_up", "use_key"
    ]
    
    cleaned = raw_text.lower().strip()
    
    # First try exact match
    if cleaned in valid_actions:
        return cleaned
    
    # Then try fuzzy match — look for the action name inside the response
    for action in valid_actions:
        if action in cleaned:
            return action
    
    # If still nothing, default to a no-op so the loop doesn't crash
    print(f"  [WARNING] Couldn't parse action from: '{raw_text}' — defaulting to move_north")
    return "move_north"


def run_loop(world, max_steps=50):
    history = []
    total_tokens = 0

    print(f"\nGoal: {world.goal_pos}")
    print("Starting agent loop...\n")

    for step in range(max_steps):

        # 1. Render the current state to terminal
        render_terminal(world)

        # 2. Get observation from the world
        obs = world.get_observation()

        # 3. Build the prompt and ask the LLM
        prompt = build_prompt(obs, history)
        raw = get_action(prompt)
        action = parse_action(raw)

        print(f"Step {step + 1}: LLM chose → {action}")

        # 4. Apply the action to the world
        result = world.step(action)
        print(f"         Result  → {result['message']}")

        # 5. Track token usage
        total_tokens += len(prompt.split()) + 5  # rough estimate
        print(f"         Tokens this run: ~{total_tokens} / 100000\n")

        # 6. Store in history
        history.append({
            "action": action,
            "result": result["message"]
        })

        # 7. Check win condition
        if world.is_done():
            render_terminal(world)
            print(f"\n✓ Goal reached in {step + 1} steps!")
            return True

        time.sleep(0.5)

    print(f"\n✗ Failed — max steps ({max_steps}) reached.")
    return False
    

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from world import World
    from tasks import load_task

    print("=== TEST 1: API CONNECTION ===")
    result = get_action("Reply with only the word: move_north")
    parsed = parse_action(result)
    print(f"Raw response:   '{result}'")
    print(f"Parsed action:  '{parsed}'")
    assert parsed == "move_north", "API connection failed or parse is broken"
    print("PASS\n")

    print("=== TEST 2: PROMPT BUILDING ===")
    task = load_task("simple_navigation")
    world = World(task["layout"])
    obs = world.get_observation()
    prompt = build_prompt(obs, [])
    assert "move_north" in prompt
    assert "VALID ACTIONS" in prompt
    print(f"Prompt length: {len(prompt)} chars")
    print("PASS\n")

    print("=== TEST 3: HISTORY IN PROMPT ===")
    fake_history = [
        {"action": "move_north", "result": "Blocked by wall."},
        {"action": "move_east",  "result": "Moved east."},
    ]
    prompt_with_history = build_prompt(obs, fake_history)
    assert "move_north" in prompt_with_history
    assert "Blocked by wall." in prompt_with_history
    print("History injected correctly")
    print("PASS\n")

    print("=== TEST 4: PARSE HANDLES BAD LLM OUTPUT ===")
    assert parse_action("I think I should move_east now") == "move_east"
    assert parse_action("MOVE_NORTH")                     == "move_north"
    assert parse_action("move_south.")                    == "move_south"
    print("PASS\n")

    print("=== TEST 5: SINGLE AGENT STEP ===")
    task = load_task("simple_navigation")
    world = World(task["layout"])
    obs = world.get_observation()
    prompt = build_prompt(obs, [])
    raw = get_action(prompt)
    action = parse_action(raw)
    result = world.step(action)
    print(f"LLM chose:  '{action}'")
    print(f"World said: '{result['message']}'")
    assert action in ["move_north","move_south","move_east","move_west","pick_up","use_key"]
    print("PASS\n")

    print("All tests passed.")