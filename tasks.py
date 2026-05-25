# tasks.py

TASKS = {
    "find_key_and_open_door": {
        "description": "Find the key and use it to open the door, then reach the goal.",
        "layout": [
            "WWWWWWWWWWWW",
            "W@.........W",
            "W..........W",
            "W..K.......W",
            "WWWWWDWWWWWW",
            "W..........W",
            "W..........W",
            "W.........GW",
            "WWWWWWWWWWWW",
        ],
    },
    "simple_navigation": {
        "description": "Navigate to the goal tile.",
        "layout": [
            "WWWWWWWW",
            "W@.....W",
            "W......W",
            "W......W",
            "W......W",
            "W.....GW",
            "WWWWWWWW",
        ],
    },
    
}

def load_task(name):
    if name not in TASKS:
        raise ValueError(f"Unknown task '{name}'. Available: {list(TASKS.keys())}")
    return TASKS[name]