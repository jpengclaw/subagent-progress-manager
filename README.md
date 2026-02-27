# Subagent Progress Manager

A specialized skill for OpenClaw that ensures you never miss a completed subagent and always provide timely progress updates.

## Overview

This skill addresses the common problem of subagents completing silently while the orchestrator forgets to check on them or update the user. It implements a cron-based progress checking system with immediate fallback on failure.

## The Problem

When you spawn a subagent and don't check its status:
- Subagent completes silently
- You don't update the user
- 15+ minutes pass with no progress
- User loses trust

## The Solution: Cron-Based Progress Checking

When you spawn ANY subagent, IMMEDIATELY create a check-in cron:

```python
from datetime import datetime, timedelta

# 1. Spawn the subagent
sessions_spawn(
    task="""...""",
    label="research-specialist",
    model="openrouter/xiaomi/mimo-v2-flash",
    runTimeoutSeconds=300
)

# 2. IMMEDIATELY create check-in cron (fires in 1 minute)
check_time = (datetime.utcnow() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
cron(action='add', job={
    "name": "check-research-specialist",
    "schedule": {"kind": "at", "at": check_time},
    "payload": {"kind": "systemEvent", "text": "CHECK_PROGRESS: research-specialist"},
    "sessionTarget": "main"
})
```

## Key Features

1. **Cron-based progress checking** - Automatic check-ins every minute
2. **Silent monitoring** - Only notify user on state change
3. **Immediate fallback** - When subagent fails, do the task yourself
4. **15-minute rule** - Kill stuck subagents after 15 minutes
5. **Progress update discipline** - Every 90 seconds

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install subagent-progress-manager
```

### Manual Installation

```bash
cp -r subagent-progress-manager ~/.openclaw/workspace/skills/
```

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 6,
        "maxConcurrent": 8,
        "runTimeoutSeconds": 480
      }
    }
  }
}
```

## Usage

### Basic Pattern

```python
# Spawn subagent with automatic progress checking
sessions_spawn(
    task="""RESEARCH SPECIALIST: ...""",
    label="research-specialist",
    model="openrouter/xiaomi/mimo-v2-flash",
    runTimeoutSeconds=300
)

# The skill automatically creates a check-in cron
# Check progress using: python3 check_progress.py --label research-specialist --action status
```

### Progress Update Schedule

| Time | Action |
|------|--------|
| 0s | Spawn specialist + create check cron |
| 60s | Cron fires, check status silently |
| 90s | Send user update (if still running) |
| 120s | Cron fires, check status |
| 180s | Send user update (if still running) |
| Completion | Update user, spawn next |
| Failure | Take over immediately, notify user |

## Scripts

### check_progress.py

Automated progress checker script:

```bash
# Check status
python3 scripts/check_progress.py --label research-specialist --action status

# Spawn with automatic cron check
python3 scripts/check_progress.py --label research-specialist --action spawn \
  --task "Research AI optimization" --timeout 300
```

## Files

- `SKILL.md` - Main skill documentation with YAML frontmatter
- `scripts/check_progress.py` - Automated progress checker
- `references/config_examples.md` - Configuration examples and templates

## Key Principles

1. **Cron is for YOU** - Silent, internal reminder
2. **Only notify user on state change** - Not every minute
3. **Reset cron if agent still busy** - Keeps check-in loop going
4. **Kill cron on completion** - Prevents unnecessary firings

## License

MIT License

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- Issues: https://github.com/jpengclaw/subagent-progress-manager/issues
- Docs: https://docs.openclaw.ai

---
*Created by Operational Neural Network*