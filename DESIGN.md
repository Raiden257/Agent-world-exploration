## Observation Representation
The agent receives the full ASCII grid plus explicit metadata:
position, inventory, key/door/goal coordinates, and directional
hints. Early versions sent only the raw grid — the agent struggled
to navigate. Adding explicit coordinates and "goal is south-east"
hints dramatically improved performance.

## Action Space
Six actions: move in 4 directions, pick_up, use_key.
Kept intentionally small — every extra action multiplies
the chance of the LLM choosing something irrelevant.
Auto-collecting the key on walk-over was added after the agent
repeatedly walked past it without picking it up.

## What Worked
- Explicit coordinate hints in the prompt (telling the agent
  exactly which row/col the key and door are on)
- Path hint logic detecting wall-blocked axes and suggesting
  the alternative direction
- Short action history in the prompt to prevent looping

## What Didn't
- Relying on the LLM to infer navigation purely from the grid
  without coordinate hints — it wandered randomly
- Large prompts — hitting Groq's token limits mid-run
  required trimming prompt length significantly
