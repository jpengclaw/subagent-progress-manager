# Config Examples

## openclaw.json Subagent Settings

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

### Field Descriptions

| Field | Default | Description |
|-------|---------|-------------|
| `maxSpawnDepth` | 1 | Allow sub-agents to spawn children (2 = orchestrator + workers) |
| `maxChildrenPerAgent` | 5 | Max active children per agent |
| `maxConcurrent` | 8 | Global concurrency lane cap |
| `runTimeoutSeconds` | 0 | Default timeout for sessions_spawn (0 = no timeout) |

## Cron Job Examples

### Check Progress Cron

```json
{
  "name": "check-research-specialist",
  "schedule": {"kind": "at", "at": "2026-02-26T23:40:00Z"},
  "payload": {"kind": "systemEvent", "text": "CHECK_PROGRESS: research-specialist"},
  "sessionTarget": "main"
}
```

### Recurring Check (Every Minute)

```json
{
  "name": "monitor-research",
  "schedule": {"kind": "every", "everyMs": 60000},
  "payload": {"kind": "systemEvent", "text": "CHECK_PROGRESS: research-specialist"},
  "sessionTarget": "main"
}
```

## sessions_spawn Example

```python
sessions_spawn(
    task="""RESEARCH SPECIALIST:
    
### TASK: Research AI optimization
### TIME: 5 min | TOKENS: 3,000
### OUTPUT: /workspace/research.md

### INSTRUCTIONS:
1. Find 5 sources
2. Write summary

### HANDOFF:
Write to /workspace/research.md""",
    label="research-specialist",
    model="openrouter/xiaomi/mimo-v2-flash",
    runTimeoutSeconds=300
)
```

## Progress Update Template

```
📊 Progress Update

Task: Research Specialist
Status: Running (65%)
Runtime: 3m 15s
Tokens: 2,450 / 3,000

Spinner: ▰▰▰▰▰▰▱▱ 60%
```

## Failure Notification Template

```
❌ Subagent Failed

Task: Research Specialist
Error: API rate limit (429)
Action: Retrying once...

⚠️ If retry fails, I will complete the task myself.
```