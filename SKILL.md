---
name: subagent-progress-manager
description: |
  Subagent progress tracking with cron-based reminders and failure recovery.
  Use when: (1) Spawning subagents for multi-step tasks, (2) Managing parallel agent workflows,
  (3) Preventing "forgotten" subagents that complete silently, (4) Ensuring progress updates
  every 90 seconds, (5) When subagent fails and you need to take over immediately.
  Key features: Automatic cron-based progress checking, immediate fallback on failure,
  90-second update discipline, subagent config optimization.
---

# Subagent Progress Manager

This skill ensures you NEVER miss a completed subagent and always provide timely progress updates.

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

## When Cron Fires (CHECK_PROGRESS Event)

When you receive `CHECK_PROGRESS: <label>`:

```python
workers = subagents(action=list, recentMinutes=2)

if workers['active']:
    # Agent still running - reset cron for another minute
    # DO NOT notify user - agent is working normally
    cron(action='add', job={
        "name": f"check-{label}",
        "schedule": {"kind": "at", "at": next_check_time},
        "payload": {"kind": "systemEvent", "text": f"CHECK_PROGRESS: {label}"},
        "sessionTarget": "main"
    })

elif completed_result:
    # Agent done - update user, spawn next specialist
    message(action='send', message="✅ Research complete. Spawning writer...")
    sessions_spawn(...)

elif failed:
    # Agent failed - update user, take over task yourself
    message(action='send', message="❌ Research failed. Doing it myself...")
    # Do the task directly - don't spawn another subagent
```

## Key Principles

1. **Cron is for YOU** - Silent, internal reminder
2. **Only notify user on state change** - Not every minute
3. **Reset cron if agent still busy** - Keeps check-in loop going
4. **Kill cron on completion** - Prevents unnecessary firings

## The 15-Minute Rule

If a subagent has been running for 15 minutes without completion:
- Kill it: `subagents(action='kill', target=sessionKey)`
- Do the task yourself
- Report failure to user

## Optimal Subagent Config

Add to openclaw.json:

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

## Progress Update Schedule

| Time | Action |
|------|--------|
| 0s | Spawn specialist + create check cron |
| 60s | Cron fires, check status silently |
| 90s | Send user update (if still running) |
| 120s | Cron fires, check status |
| 180s | Send user update (if still running) |
| Completion | Update user, spawn next |
| Failure | Take over immediately, notify user |

## Immediate Fallback Rule

**When subagent fails:**
1. DO NOT spawn another subagent to retry
2. Do the task YOURSELF immediately
3. Notify user what happened
4. Complete the task

This prevents infinite retry loops and ensures tasks complete.

## Scripts

See [scripts/check_progress.py](scripts/check_progress.py) for the automated check script.

## References

See [references/config_examples.md](references/config_examples.md) for config templates.