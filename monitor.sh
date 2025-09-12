#!/bin/bash
# Flight Tracker Health Monitor (Lightsail)
# - Ensures service is running and responsive
# - Auto-restarts on failure
# - Throttles Discord alerts (per issue key)
# - Attaches last 50 lines of logs on failure
# - Avoids overlapping runs with a lock

set -euo pipefail

SERVICE_NAME="flight-tracker"
HEALTH_URL="http://localhost:8000/health"
STATE_DIR="/var/tmp/flight-tracker-monitor"
LOCKFILE="/tmp/flight-tracker-monitor.lock"
THROTTLE_SECONDS=600   # 10 minutes
LOG_LINES=50

# Webhook comes from environment or .env; alerts are skipped if unset
DISCORD_WEBHOOK="${DISCORD_WEBHOOK_URL:-}"

# Try to load .env if not set in environment
if [[ -z "$DISCORD_WEBHOOK" ]]; then
  ENV_FILE="/home/ubuntu/flight-tracker/.env"
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    . "$ENV_FILE"
    set +a
    DISCORD_WEBHOOK="${DISCORD_WEBHOOK_URL:-$DISCORD_WEBHOOK}"
  fi
fi

mkdir -p "$STATE_DIR"

# Single-run lock
exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "Another monitor run is active. Exiting."
  exit 0
fi

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Throttled alert sender
should_send_alert() {
  local key="$1"
  local stamp_file="${STATE_DIR}/${key}.last"
  local now_epoch last_epoch
  now_epoch=$(date +%s)
  if [[ -f "$stamp_file" ]]; then
    last_epoch=$(cat "$stamp_file" || echo 0)
  else
    last_epoch=0
  fi
  if (( now_epoch - last_epoch >= THROTTLE_SECONDS )); then
    echo "$now_epoch" > "$stamp_file"
    return 0
  fi
  return 1
}

json_escape() {
  # Escapes JSON special chars
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || \
  awk '{gsub(/\\/,"\\\\"); gsub(/"/,"\\\""); gsub(/\t/,"\\t"); gsub(/\r/,"\\r"); gsub(/\n/,"\\n"); print}'
}

send_discord() {
  local content="$1"
  local key="${2:-generic}"

  # If no webhook configured, skip gracefully
  if [[ -z "$DISCORD_WEBHOOK" ]]; then
    return 0
  fi

  if should_send_alert "$key"; then
    local payload
    payload="{\"content\": $(printf "%s" "$content" | json_escape)}"
    curl -sS -X POST "$DISCORD_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "$payload" >/dev/null || true
  fi
}

send_discord_with_logs() {
  local message="$1"
  local key="$2"

  # If no webhook configured, skip gracefully
  if [[ -z "$DISCORD_WEBHOOK" ]]; then
    return 0
  fi

  local logs
  logs=$(journalctl -u "$SERVICE_NAME" -n "$LOG_LINES" --no-pager 2>&1 | tail -n "$LOG_LINES")
  local combined="${message}\n\nLast ${LOG_LINES} lines of logs:\n\`\`\`\n${logs}\n\`\`\`"
  send_discord "$combined" "$key"
}

# 1) Ensure systemd service status
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
  send_discord "❌ $(timestamp) Flight Tracker service is DOWN! Attempting restart..." "svc_down"
  systemctl restart "$SERVICE_NAME" || true
  sleep 5
fi

# 2) Health check (HTTP)
if ! curl -sS --connect-timeout 10 --max-time 15 "$HEALTH_URL" >/dev/null; then
  send_discord_with_logs "🚨 $(timestamp) Health check failed. Restarting service..." "health_fail"
  systemctl restart "$SERVICE_NAME" || true
  sleep 6
  if ! curl -sS --connect-timeout 10 --max-time 15 "$HEALTH_URL" >/dev/null; then
    send_discord_with_logs "💥 $(timestamp) Service failed to recover after restart. Manual intervention required." "health_still_fail"
    # don't exit non-zero to keep cron quiet
  else
    send_discord "✅ $(timestamp) Service recovered after restart." "recovered"
  fi
fi

# 3) Resource checks (memory/disk)
# Memory %
MEMORY=$(free | awk '/Mem/{printf "%.1f", $3/$2*100}')
# Disk % on root
DISK=$(df / | awk 'END{gsub(/%/,"",$5); print $5}')

# Requires bc; if missing, skip thresholds gracefully
if command -v bc >/dev/null 2>&1; then
  if (( $(echo "$MEMORY > 80" | bc -l) )) || (( DISK > 90 )); then
    send_discord "⚠️ $(timestamp) High resource usage: Memory ${MEMORY}%, Disk ${DISK}%." "high_resource"
  fi
fi

# 4) Optional: stale health detection
# Record last successful health check timestamp
if curl -sS --connect-timeout 5 --max-time 10 "$HEALTH_URL" >/dev/null; then
  date +%s > "${STATE_DIR}/last_health_ok.epoch"
else
  # If last ok was > 30 minutes ago, alert (throttled)
  if [[ -f "${STATE_DIR}/last_health_ok.epoch" ]]; then
    now=$(date +%s)
    last_ok=$(cat "${STATE_DIR}/last_health_ok.epoch" || echo 0)
    if (( now - last_ok > 1800 )); then
      send_discord_with_logs "⏰ $(timestamp) Health has been failing for >30 minutes." "health_stale"
    end
  fi
fi

echo "$(timestamp): Monitor run complete. Mem=${MEMORY}% Disk=${DISK}%"