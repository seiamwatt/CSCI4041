#!/usr/bin/env python3
"""
Real-time animated bar chart with Rich Live.
Run:  pip install rich && python live_bars.py
Exit: Ctrl+C
"""

import math
import random
import time
from datetime import datetime

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# ── Config ──────────────────────────────────────
SERVICES = ["API Gateway", "Auth", "Database", "Cache", "ML Engine", "Queue", "CDN", "Scheduler"]
BAR_WIDTH = 40
REFRESH_HZ = 10  # updates per second

# Each service gets a base value + some wave/noise behavior
bases = [random.uniform(20, 80) for _ in SERVICES]
speeds = [random.uniform(0.3, 1.5) for _ in SERVICES]


def get_bar_style(pct: float) -> str:
    if pct > 90:
        return "bold red"
    elif pct > 70:
        return "yellow"
    elif pct > 40:
        return "bright_cyan"
    else:
        return "green"


def build_chart(tick: int) -> Panel:
    t = tick / REFRESH_HZ  # time in seconds

    table = Table(
        box=None,
        show_header=True,
        header_style="bold bright_cyan",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("SERVICE", min_width=12, style="bold white")
    table.add_column("", ratio=1)  # bar
    table.add_column("RPS", justify="right", min_width=8)
    table.add_column("Δ", justify="right", min_width=6)

    for i, name in enumerate(SERVICES):
        # Sine wave + noise for organic movement
        wave = math.sin(t * speeds[i] + i * 1.2) * 20
        noise = random.uniform(-3, 3)
        pct = max(5, min(100, bases[i] + wave + noise))

        # Slowly drift base values
        bases[i] += random.uniform(-0.1, 0.1)
        bases[i] = max(15, min(85, bases[i]))

        filled = int(pct / 100 * BAR_WIDTH)
        empty = BAR_WIDTH - filled
        style = get_bar_style(pct)

        bar = Text()
        bar.append("█" * filled, style=style)
        bar.append("░" * empty, style="bright_black")

        rps = int(pct * 127)  # fake requests/sec
        delta = random.choice(["↑", "↓", " "]) + f"{abs(random.randint(1, 200))}"
        delta_style = "green" if delta.startswith("↑") else "red" if delta.startswith("↓") else "bright_black"

        table.add_row(name, bar, f"{rps:,}", Text(delta, style=delta_style))

    now = datetime.now().strftime("%H:%M:%S")
    return Panel(
        table,
        title=f"[bold bright_cyan]◆ Live Traffic — Requests/sec[/]",
        subtitle=f"[bright_black]{now}  ·  Ctrl+C to exit[/]",
        border_style="bright_cyan",
        box=box.DOUBLE,
        padding=(1, 2),
    )


if __name__ == "__main__":
    tick = 0
    with Live(build_chart(tick), console=console, refresh_per_second=REFRESH_HZ, screen=True) as live:
        try:
            while True:
                tick += 1
                live.update(build_chart(tick))
                time.sleep(1 / REFRESH_HZ)
        except KeyboardInterrupt:
            pass

    console.print("\n[bright_black]Dashboard stopped.[/]")