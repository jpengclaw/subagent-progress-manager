#!/usr/bin/env python3
"""
Subagent Progress Checker

Usage:
    python3 check_progress.py --label research-specialist --action status

Actions:
    status    - Check if subagent is still running
    spawn     - Spawn subagent with automatic cron check
    kill      - Kill a stuck subagent
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta


def get_subagent_status(label: str) -> dict:
    """Check if subagent with given label is active."""
    result = subprocess.run(
        ["openclaw", "subagents", "--json"],
        capture_output=True,
        text=True
    )
    
    try:
        data = json.loads(result.stdout)
        for agent in data.get("recent", []):
            if label in agent.get("label", ""):
                return {
                    "status": agent.get("status", "unknown"),
                    "runtime": agent.get("runtime", "0m"),
                    "tokens": agent.get("totalTokens", 0)
                }
    except:
        pass
    
    return {"status": "not_found"}


def spawn_with_cron(task: str, label: str, model: str, timeout: int):
    """Spawn subagent and create check-in cron."""
    # Spawn the subagent
    spawn_cmd = [
        "openclaw", "subagents", "spawn",
        "--task", task,
        "--label", label,
        "--model", model,
        "--timeout", str(timeout)
    ]
    
    print(f"✅ Spawning subagent: {label}")
    subprocess.run(spawn_cmd)
    
    # Create check cron (1 minute from now)
    check_time = (datetime.utcnow() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    cron_cmd = [
        "openclaw", "cron", "add",
        "--name", f"check-{label}",
        "--schedule", f"at:{check_time}",
        "--payload", f"CHECK_PROGRESS:{label}",
        "--session", "main"
    ]
    
    print(f"⏰ Created check cron for {check_time}")
    subprocess.run(cron_cmd)
    
    print(f"✅ Subagent + cron check scheduled for '{label}'")


def kill_subagent(label: str):
    """Kill a stuck subagent."""
    result = subprocess.run(
        ["openclaw", "subagents", "--json"],
        capture_output=True,
        text=True
    )
    
    try:
        data = json.loads(result.stdout)
        for agent in data.get("recent", []):
            if label in agent.get("label", ""):
                session_key = agent.get("sessionKey", "")
                print(f"🛑 Killing subagent: {session_key}")
                subprocess.run(["openclaw", "subagents", "kill", "--session", session_key])
                return
    except:
        pass
    
    print(f"⚠️ No subagent found with label: {label}")


def main():
    parser = argparse.ArgumentParser(description="Subagent Progress Manager")
    parser.add_argument("--label", help="Subagent label to check/spawn/kill")
    parser.add_argument("--action", choices=["status", "spawn", "kill"], default="status")
    parser.add_argument("--task", help="Task description for spawn")
    parser.add_argument("--model", default="openrouter/xiaomi/mimo-v2-flash")
    parser.add_argument("--timeout", type=int, default=300)
    
    args = parser.parse_args()
    
    if args.action == "status":
        if args.label:
            status = get_subagent_status(args.label)
            print(json.dumps(status, indent=2))
        else:
            print("❌ --label required for status check")
            sys.exit(1)
    
    elif args.action == "spawn":
        if args.label and args.task:
            spawn_with_cron(args.task, args.label, args.model, args.timeout)
        else:
            print("❌ --label and --task required for spawn")
            sys.exit(1)
    
    elif args.action == "kill":
        if args.label:
            kill_subagent(args.label)
        else:
            print("❌ --label required for kill")
            sys.exit(1)


if __name__ == "__main__":
    main()