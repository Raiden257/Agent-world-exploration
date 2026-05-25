# renderer.py
from rich.console import Console
from rich.text import Text

console = Console()

TILE_STYLES = {
    '@': ('bright_green',  '@'),
    'K': ('bright_yellow', 'K'),
    'D': ('bright_red',    'D'),
    'G': ('bright_cyan',   'G'),
    'W': ('grey50',        'W'),
    '.': ('grey30',        '.'),
}

def render_terminal(world):
    console.rule(f"Step {world.steps_taken}")
    for row in world.grid:
        line = Text()
        for cell in row:
            style, char = TILE_STYLES.get(cell, ('white', cell))
            line.append(char + ' ', style=style)
        console.print(line)
    console.print(f"Inventory: {world.inventory or 'empty'}")