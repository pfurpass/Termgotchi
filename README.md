# 🐾 ServerPet

> A Tamagotchi-style virtual pet that lives in your terminal and reflects the health of your server.

```
   /\_/\
  ( ^ω^ )    Name: Byte       Health:    ████████████ 92%
   > ♥ <     Mood:  Happy     Hunger:    ████████░░░░ 68%
             Age:   3.2 days  CPU:       ████████░░░░ 31%
```

ServerPet turns boring system monitoring into a living creature you must care for.
If your server suffers, so does your pet. Keep your system healthy — keep your pet happy.

---

## Installation

```bash
git clone https://github.com/yourname/serverpet.git
cd serverpet
pip install -e .
```

That's it. The `serverpet` command is now available globally.

> **Requires Python 3.10+**

---

## Quick Start

```bash
# Hatch your first pet
serverpet start --name Byte --species cat --personality cheerful

# Open the live dashboard
serverpet watch

# Quick status check
serverpet status
```

---

## Commands

| Command | Description |
|---|---|
| `start` | Hatch a new pet |
| `status` | Snapshot of pet stats + system metrics |
| `watch` | **Live dashboard** — auto-refreshes every 2.5 seconds |
| `feed` | Reduce hunger |
| `clean` | Restore cleanliness |
| `play` | Mini-game — boosts happiness |
| `sleep` | Rest the pet and restore energy |
| `doctor` | Emergency heal |
| `stats` | Detailed system metrics table |
| `achievements` | Achievement board |
| `rename <n>` | Give the pet a new name |
| `theme <theme>` | Switch color theme |
| `reset` | Delete the pet and start fresh |
| `info` | Full command reference |

### `start` options

```bash
serverpet start \
  --name        Byte      \   # Pet name          (default: Byte)
  --species     cat       \   # See Species below  (default: cat)
  --personality cheerful  \   # See Personalities  (default: random)
  --reset                     # Delete existing pet first
```

### `sleep` options

```bash
serverpet sleep --duration 12   # Simulate 12 hours of rest
```

---

## Live Dashboard

```bash
serverpet watch
```

```
╭─────────────────── 🐾 ServerPet Watch — Byte ────────────────────╮
│                                                                   │
│    /\_/\                                                          │
│   ( ^ω^ )     Name      Byte  (Cat · Cheerful)                   │
│    > ♥ <      Mood      😊 Happy                                  │
│               Age       3.2 days  🏆 2 achievements              │
│                                                                   │
│   Health      [████████████████]  94.0%                          │
│   Hunger      [█████████████░░░]  82.0%                          │
│   Energy      [████████████░░░░]  74.0%                          │
│   Happiness   [██████████████░░]  88.0%                          │
│   Cleanness   [███████████░░░░░]  68.0%                          │
│                                                                   │
│   ── System ─────────────────────────────────────                │
│   CPU         [████████████████]  23.0%                          │
│   RAM         [████████████░░░░]  54.0%                          │
│   Disk        [██████████░░░░░░]  60.0%                          │
│   Processes   182                                                 │
│   Uptime      2d 4h 17m                                          │
│                                                                   │
│   ── Alerts ─────────────────────────────────────                │
│   ✅  All systems nominal                                         │
│                                                                   │
│   Updated 14:32:01 · Ctrl+C to exit                              │
╰───────────────────────────────────────────────────────────────────╯
```

Press `Ctrl+C` to exit.

---

## How System Metrics Map to Your Pet

| System Condition | Pet Effect |
|---|---|
| CPU > 65% (energetic personality) | Pet becomes hyperactive ⚡ |
| CPU > 90% | Pet gets angry / stressed 😠 |
| RAM > 90% | Energy drains faster |
| Disk > 75% | Hunger increases faster |
| Disk > 95% | Health begins to drop |
| All stable | Happiness climbs naturally 😊 |
| High hunger + low cleanliness | Health declines |
| Good conditions over time | Pet naturally recovers |

If **health reaches 0**, the pet dies. Use `serverpet start --reset` to begin again.

---

## Species

| Species | Description |
|---|---|
| `cat` | Classic feline companion |
| `robot` | Mechanical monitor with status displays |
| `blob` | Simple, expressive blob creature |
| `alien` | Extraterrestrial system watcher |
| `dragon` | Powerful winged guardian |

Each species has **11 unique mood states** rendered in ASCII art.

---

## Personalities

Personalities change how fast pet stats decay and how the pet reacts to events.

| Personality | Behaviour |
|---|---|
| `cheerful` | Upbeat reactions, small happiness bonus |
| `dramatic` | Exaggerates everything — every crisis is a catastrophe |
| `lazy` | Hungers slowly, loses energy faster |
| `energetic` | Loves high CPU activity, consumes energy quickly |
| `grumpy` | Slow happiness gain, sharp dialogue |
| `stoic` | Calm and clinical. No complaints. |

---

## Pet Attributes

| Attribute | Meaning | Drains when… |
|---|---|---|
| **Health** | Overall wellbeing | CPU/RAM/Disk are critical, hunger/cleanliness are low |
| **Hunger** | How fed the pet is | Over time; faster with high disk usage |
| **Energy** | How rested the pet is | Over time; faster with high CPU |
| **Happiness** | Mood quality | Hunger/cleanliness are low; naturally rises when stable |
| **Cleanliness** | Hygiene level | Slowly over time; faster with high RAM |

---

## Mood States

| Mood | Trigger |
|---|---|
| 😊 Happy | Health > 80, happiness > 80 |
| 😌 Content | Normal healthy state |
| 😢 Sad | Happiness < 30 or cleanliness < 20 |
| 😠 Angry | CPU > 90% or RAM > 90% |
| ⚡ Hyperactive | CPU > 65% + energetic personality |
| 😴 Sleeping | Energy < 20% |
| 🤒 Sick | Health < 35% |
| 😋 Hungry | Hunger > 80% |
| 💀 Dying | Health < 15% |

---

## Mini-Game

Running `serverpet play` launches a **number guessing game**:

- Guess a number between 1 and 10
- 3 attempts with high/low hints
- **Win:** +25 happiness
- **Lose:** +5 happiness (for trying!)
- Win 10 games to unlock the 🎮 **Gamer** achievement

---

## Achievements

| Achievement | Icon | Requirement |
|---|---|---|
| Server Whisperer | 🏆 | System uptime ≥ 30 days |
| Pet Doctor | 💊 | Heal the pet 10 times |
| Clean Server | ✨ | Disk under 40% for 7 days |
| Joy Machine | 😊 | Pet happy for 24 hours straight |
| Night Owl | 🦉 | Check on the pet at midnight |
| Gamer | 🎮 | Win 10 mini-games |
| Survivor | 💪 | Pet recovers from critical health |
| Old Friend | 🌟 | Pet reaches 30 days old |

---

## Color Themes

```bash
serverpet theme matrix    # Green-on-black hacker aesthetic
serverpet theme sunset    # Warm magenta and yellow
serverpet theme ocean     # Cool blues and cyan
serverpet theme hacker    # Bold bright green
serverpet theme default   # The classic cyan/green look
```

---

## Persistence

Pet state is saved to `~/.serverpet/state.json` after every command. The pet **ages in real time** and stats decay between sessions based on elapsed time (capped at 2 hours per gap to avoid punishing long absences).

---

## Typical Care Routine

```bash
serverpet status    # Morning check-in
serverpet feed      # If hungry
serverpet clean     # If dirty
serverpet sleep     # If low energy
serverpet doctor    # If health is dropping
serverpet play      # For fun (and achievements)
serverpet watch     # Leave running on a spare terminal
```

---

## Project Structure

```
serverpet/
├── serverpet/
│   ├── __init__.py
│   └── __main__.py     # All application logic
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## License

MIT — do whatever you want with it. 🐾
