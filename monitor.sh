if ! systemctl is-active --quiet flight-tracker; then

    curl -X POST "https://discord.com/api/webhooks/1414723721184411771/cNViB_v4UFJ3k-EN5UpPjRea3MgGuxeQwJL-w9txczsVx7tf3OfHXVBFVSKfGf7C3UUL" \
         -H "Content type: application/json" \
         -d '{"content": Flight Tracker service is DOWN!}'


systemctl restart flight_tracker
fi

MEMORY=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
DISK=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if (( $(echo "$MEMORY > 80" | bc-l) )) || (( DISK > 90 )); then
    curl -X POST "https://discord.com/api/webhooks/1414723721184411771/cNViB_v4UFJ3k-EN5UpPjRea3MgGuxeQwJL-w9txczsVx7tf3OfHXVBFVSKfGf7C3UUL" \
         -H "Content-Type: application/json" \
         -d "{\"content\":\"High resource usage: Memory ${MEMORY}%, Disk ${DISK}%\"}"
fi