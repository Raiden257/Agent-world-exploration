import numpy as np
import copy

# Tile types — what each cell in the grid can be
EMPTY = "."
WALL = "W"
AGENT = "@"
KEY = "K"
DOOR = "D"
GOAL = "G"


class World:
    def __init__(self, layout):
        """
        __init__ runs automatically when you do World(layout).
        It sets up all the starting values.
        """
        self.grid = [list(row) for row in layout]  # 2D list of tile characters
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.inventory = []  # items the agent is carrying
        self.door_locked = True
        self.steps_taken = 0
        self.agent_pos = self._find(AGENT)  # locate @ on the grid
        self.goal_pos = self._find(GOAL)

    def _find(self, tile):
        """Scan the grid and return (row, col) of a given tile."""
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == tile:
                    return (r, c)
        return None

    def get_observation(self):
        r, c = self.agent_pos
        gr, gc = self.goal_pos

        # Find key and door positions
        key_pos  = self._find(KEY)
        door_pos = self._find(DOOR)

        row_hint = "south" if gr > r else "north" if gr < r else "same row"
        col_hint = "east"  if gc > c else "west"  if gc < c else "same column"

        grid_lines = [' '.join(row) for row in self.grid]
        grid_str = '\n'.join(grid_lines)

        text = f"""Grid (rows increase going south, cols increase going east):
    {grid_str}

    Your position:  row {r}, col {c}
    Key position:   {f'row {key_pos[0]}, col {key_pos[1]}' if key_pos else 'collected'}
    Door position:  {f'row {door_pos[0]}, col {door_pos[1]}' if door_pos else 'open'}
    Goal position:  row {gr}, col {gc}
    Goal is:        {row_hint} and {col_hint} from you
    Inventory:      {self.inventory if self.inventory else 'empty'}
    """
        return {
            "text": text,
            "position": self.agent_pos,
            "inventory": self.inventory,
            "key_pos": key_pos,
            "door_pos": door_pos,
            "goal_pos": self.goal_pos,
            "grid": self.grid,
            "step": self.steps_taken
        }

    def step(self, action):
        """
        Apply an action to the world.
        Returns a dict with success (bool) and message (str).
        """
        self.steps_taken += 1
        action = action.strip().lower()

        if action in ("move_north", "move_south", "move_east", "move_west"):
            return self._move(action)
        elif action == "pick_up":
            return self._pick_up()
        elif action == "use_key":
            return self._use_key()
        else:
            return {"success": False, "message": f"Unknown action: '{action}'"}

    def _move(self, direction):
        r, c = self.agent_pos
        deltas = {
            'move_north': (-1,  0),
            'move_south': ( 1,  0),
            'move_east':  ( 0,  1),
            'move_west':  ( 0, -1),
        }
        dr, dc = deltas[direction]
        new_r, new_c = r + dr, c + dc

        if not (0 <= new_r < self.height and 0 <= new_c < self.width):
            return {"success": False, "message": "Can't move — edge of world."}

        target = self.grid[new_r][new_c]

        if target == WALL:
            return {"success": False, "message": "Blocked by wall."}

        if target == DOOR:
            if self.door_locked and 'key' not in self.inventory:
                return {"success": False, "message": "Door is locked. Get the key first."}
            if self.door_locked and 'key' in self.inventory:
                self.inventory.remove('key')
                self.door_locked = False
                self.grid[r][c] = EMPTY
                self.grid[new_r][new_c] = AGENT
                self.agent_pos = (new_r, new_c)
                print("  [AUTO] Key used — door open!")
                return {"success": True, "message": "Used key, door now open, moved through."}

        if target == KEY:
            self.inventory.append('key')
            print("  [AUTO] Key picked up!")

        self.grid[r][c] = EMPTY
        self.grid[new_r][new_c] = AGENT
        self.agent_pos = (new_r, new_c)
        return {"success": True, "message": f"Moved {direction.split('_')[1]}."}

    def _use_key(self):
        """Use the key if standing next to the door."""
        if "key" not in self.inventory:
            return {"success": False, "message": "You don't have a key."}
        r, c = self.agent_pos
        for dr, dc in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                if self.grid[nr][nc] == DOOR:
                    self.grid[nr][nc] = EMPTY
                    self.door_locked = False
                    self.inventory.remove("key")
                    return {"success": True, "message": "Used key — door is now open!"}
        return {"success": False, "message": "No door nearby to use key on."}

    def _is_at_goal(self):
        return self.agent_pos == self.goal_pos

    def is_done(self):
        return self._is_at_goal()

    def reset(self, layout):
        """Restart the world with a fresh layout."""
        self.__init__(layout)


if __name__ == "__main__":
    # A simple test layout — paste your own
    test_layout = [
        "........",
        ".@..K...",
        "....WWWW",
        "........",
        "......DG",
    ]
    world = World(test_layout)
    print(world.get_observation()["text"])

    result = world.step("move_east")
    print(result["message"])

    result = world.step("pick_up")
    print(result["message"])
    print("Inventory:", world.inventory)
