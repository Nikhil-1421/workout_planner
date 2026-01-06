# IronLog - Premium Workout Tracker

A sleek, dark-themed, minimalist workout tracker iOS app built with Python and BeeWare/Toga.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-iOS-lightgrey.svg)

## Features

- **Workout Templates**: Create, edit, and reuse workout routines
- **Quick Start**: Begin a workout in under 5 seconds
- **Session Timer**: Accurate timer with pause/resume, persists across app restarts
- **Frictionless Logging**: Quick-add chips, smart defaults, numeric keypads
- **Offline-First**: SQLite persistence, works without connectivity
- **History**: Browse past sessions with full details
- **Export**: JSON and CSV export for any session
- **Premium UX**: Dark theme, minimal clutter, large tap targets

## Quick Start (Codespaces)

### One-Command Bootstrap

```bash
./scripts/bootstrap.sh
```

This installs all dependencies and sets up the development environment.

### Run Development Server

```bash
./scripts/run_dev.sh
```

Or manually:

```bash
briefcase dev
```

### Run Tests

```bash
./scripts/test.sh
```

### Lint Code

```bash
./scripts/lint.sh
```

## Project Structure

```
workout-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # App entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── tabs.py          # Tab bar navigation container
│   │   ├── home.py          # Home tab - quick start
│   │   ├── session.py       # Active workout session
│   │   ├── exercise_detail.py  # Set logging for an exercise
│   │   ├── templates.py     # Template management
│   │   ├── history.py       # Past sessions
│   │   ├── settings.py      # Export, app info, reset
│   │   ├── theme.py         # Colors, fonts, spacing
│   │   └── components.py    # Reusable UI components
│   ├── core/
│   │   ├── __init__.py
│   │   ├── timer.py         # Session timer logic
│   │   ├── models.py        # Dataclasses for domain objects
│   │   └── export.py        # JSON/CSV export
│   └── data/
│       ├── __init__.py
│       ├── db.py            # SQLite connection management
│       ├── migrations.py    # Schema versioning
│       └── repositories.py  # Data access layer
├── tests/
│   ├── __init__.py
│   ├── test_timer.py
│   ├── test_repositories.py
│   └── test_export.py
├── scripts/
│   ├── bootstrap.sh
│   ├── run_dev.sh
│   ├── lint.sh
│   └── test.sh
├── .devcontainer/
│   └── devcontainer.json
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Development

### Prerequisites

- Python 3.11+
- pip

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Run development server
briefcase dev
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with ruff
ruff format .

# Type check with mypy
mypy app/

# Run tests
pytest
```

## iOS Build & Deployment

### Important: macOS Required

While development and testing can happen in GitHub Codespaces (Linux), **iOS app signing and deployment requires macOS with Xcode**.

### Development in Codespaces

1. Write and test code in Codespaces
2. Run `briefcase dev` for desktop preview
3. Run tests with `pytest`
4. Commit and push changes

### Mac Handoff for iOS Build

On your Mac with Xcode installed:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/workout-tracker.git
cd workout-tracker

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create iOS project
briefcase create iOS

# 4. Build iOS app
briefcase build iOS

# 5. Run in iOS Simulator
briefcase run iOS

# 6. Package for App Store (requires Apple Developer account)
briefcase package iOS --adhoc  # For testing
# OR
briefcase package iOS  # For App Store submission
```

### iOS Signing Setup

1. Open Xcode and sign in with your Apple ID
2. Create an iOS Development certificate
3. Register your test devices
4. Create a provisioning profile
5. Update `pyproject.toml` with your bundle identifier and team ID

```toml
[tool.briefcase.app.ironlog.iOS]
bundle_identifier = "com.yourcompany.ironlog"
# team_id = "YOUR_TEAM_ID"  # Uncomment and set for distribution
```

### Simulator Notes

- The app runs best on iPhone 14 Pro simulator or newer
- Use `briefcase run iOS --device "iPhone 14 Pro"` to specify device
- For older simulators, UI may need adjustment

## Architecture

### UI Layer (`app/ui/`)

- **Toga-based** declarative UI
- Tab bar navigation with 4 tabs: Home, Templates, History, Settings
- Dark theme with premium aesthetics
- Responsive layouts with generous spacing

### Core Layer (`app/core/`)

- **Timer**: Accurate timing with background persistence
- **Models**: Clean dataclasses for domain objects
- **Export**: JSON and CSV generation

### Data Layer (`app/data/`)

- **SQLite** for offline-first persistence
- **Migrations**: Safe schema evolution
- **Repositories**: Clean separation of data access

## Data Model

### Tables

- `workout_templates`: Saved workout routines
- `template_exercises`: Exercises within templates
- `workout_sessions`: Completed or active workouts
- `session_exercises`: Exercises within a session
- `sets`: Individual sets logged
- `app_state`: Key-value store for app state

### Migrations

Schema versioning with forward-only migrations applied at startup.

## Preloaded Templates

The app ships with 3 example templates:

1. **Push Day**: Bench Press, Overhead Press, Incline Dumbbell Press, Tricep Pushdowns, Lateral Raises
2. **Pull Day**: Deadlift, Barbell Rows, Pull-ups, Face Pulls, Bicep Curls
3. **Leg Day**: Squats, Romanian Deadlifts, Leg Press, Leg Curls, Calf Raises

## Export Formats

### JSON

```json
{
  "session_id": "uuid",
  "template_name": "Push Day",
  "started_at": "2024-01-15T10:00:00",
  "ended_at": "2024-01-15T11:30:00",
  "duration_seconds": 5400,
  "exercises": [
    {
      "name": "Bench Press",
      "uses_weight": true,
      "sets": [
        {"reps": 8, "weight": 135.0, "created_at": "..."},
        {"reps": 8, "weight": 135.0, "created_at": "..."}
      ]
    }
  ]
}
```

### CSV

```csv
exercise,set_number,reps,weight,created_at
Bench Press,1,8,135.0,2024-01-15T10:05:00
Bench Press,2,8,135.0,2024-01-15T10:08:00
...
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ using Python and BeeWare
