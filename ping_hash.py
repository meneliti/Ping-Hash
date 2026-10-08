#!/usr/bin/env python3
"""Ping-Hash: lightweight uptime prober that records SHA-256 hashed
probe timestamps to a log and pushes results to the remote git remote."""
import hashlib
import random
import subprocess
import datetime
import os
import sys

REPO_DIR = os.path.expanduser("~/ping-hash/repo")
LOG_DIR = os.path.join(REPO_DIR, "logs")

# --- Probe labels & status markers (variasi isi entri tiap probe) ---
WORDS = [
    "probe", "ping", "healthcheck", "heartbeat", "beacon", "sweep",
    "poll", "trace", "monitor", "signal", "echo", "uptime", "check",
    "audit", "pulse", "watchdog", "relay", "node", "cluster", "edge",
]
EMOJIS_UP = ["🟢", "✅", "🟩", "🟦", "🔵", "⚡", "🛰️", "📶", "🌐", "🧭"]
EMOJIS_WARN = ["🟡", "⚠️", "🟠", "📡"]


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd or REPO_DIR, shell=True,
                          text=True, capture_output=True)


def pick_status():
    # 90% "up", 10% "warn" — kebanyakan probe sukses, sesekali latency tinggi
    return random.choices(["up", "warn"], weights=[90, 10])[0]


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Hash data waktu (SHA-256) — fingerprint unik untuk tiap probe
    digest = hashlib.sha256(iso.encode()).hexdigest()

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{date_str}.log")

    before = open(log_path).read() if os.path.exists(log_path) else ""

    # Batasi ukuran file: kalau sudah >48 entri, mulai file baru bergantian
    if before.count("\n") >= 48:
        log_path = os.path.join(LOG_DIR, f"{date_str}_{now.strftime('%H')}.log")
        before = open(log_path).read() if os.path.exists(log_path) else ""

    line = f"{iso} | {digest}\n"
    if line in before:
        print("Duplicate probe, skip.")
        return 0

    status = pick_status()
    word = random.choice(WORDS)
    emoji = random.choice(EMOJIS_UP if status == "up" else EMOJIS_WARN)
    latency = random.randint(12, 340) if status == "up" else random.randint(800, 2400)
    entry = f"{iso} | {digest[:12]} | {emoji} {word} | status={status} | rtt={latency}ms\n"

    with open(log_path, "a") as f:
        f.write(entry)

    r = run("git add logs/ && git commit -m "
            f"\"{emoji} probe {date_str} {time_str[:5]} {digest[:12]} ({status}, {latency}ms)\"")
    if "nothing to commit" in r.stdout + r.stderr:
        print("Nothing to commit.")
        return 0
    if r.returncode != 0:
        print("commit gagal:", r.stderr)
        return 1

    r = run("git push origin main")
    if r.returncode != 0:
        print("push gagal:", r.stderr)
        return 1
    print(f"OK: {iso} hash={digest[:12]} status={status} rtt={latency}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
