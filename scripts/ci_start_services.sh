#!/usr/bin/env bash
set -euo pipefail

# Start the simulated helper and a static webserver, then wait for both to report readiness.

ART_DIR=test-artifacts
mkdir -p "$ART_DIR"

PORT_HELPER=${PORT_HELPER:-5001}
PORT_WEBSERVER=${PORT_WEBSERVER:-5000}

echo "Starting simulated helper and http-server (helper:$PORT_HELPER web:$PORT_WEBSERVER)"

node tests/helpers/simulated_helper.js > "$ART_DIR/simulated_helper.log" 2>&1 &
HELPER_PID=$!

npx http-server ./webapp -p "$PORT_WEBSERVER" -c-1 > "$ART_DIR/webserver.log" 2>&1 &
WEBSERVER_PID=$!

echo "helper pid=$HELPER_PID webserver pid=$WEBSERVER_PID"

START=$(date +%s)
TIMEOUT=${TIMEOUT:-300}
END=$((START+TIMEOUT))

check_http() {
  local url=$1
  # return non-empty if HTTP code is available (any code except 000)
  code=$(curl -sS -o /dev/null -w '%{http_code}' --connect-timeout 2 --max-time 3 "$url" || true)
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    echo "$code"
    return 0
  fi
  return 1
}

check_helper_health() {
  local url=$1
  local tmpbody="$ART_DIR/helper_health.json"
  local status
  local probe_token="PROBE_YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
  status=$(curl -sS -H "X-TowerScout-Operation-Authorization: $probe_token" -w '%{http_code}' -o "$tmpbody" --connect-timeout 2 --max-time 3 "$url" || echo "000")
  if [ "$status" = "200" ] && grep -q '"state":"ready"' "$tmpbody"; then
    return 0
  fi
  return 1
}

while [ $(date +%s) -lt $END ]; do
  # ensure helper process still alive
  if ! kill -0 $HELPER_PID 2>/dev/null; then
    echo "Helper process $HELPER_PID exited unexpectedly" >&2
    echo "--- simulated_helper.log (tail) ---" >&2
    tail -n 200 "$ART_DIR/simulated_helper.log" >&2 || true
    exit 1
  fi


  helper_ok=1
  web_ok=1

  if check_helper_health "http://127.0.0.1:${PORT_HELPER}/health" 2>/dev/null || check_helper_health "http://localhost:${PORT_HELPER}/health" 2>/dev/null; then
    helper_ok=0
  fi

  if check_http "http://127.0.0.1:${PORT_WEBSERVER}" 2>/dev/null || check_http "http://localhost:${PORT_WEBSERVER}" 2>/dev/null; then
    web_ok=0
  fi

  if [ $helper_ok -eq 0 ] && [ $web_ok -eq 0 ]; then
    echo "All services are responding"
    exit 0
  fi

  sleep 1
done

echo "Timeout waiting for helper or webserver" >&2
echo "--- simulated_helper.log (tail) ---" >&2
test -f "$ART_DIR/simulated_helper.log" && tail -n 200 "$ART_DIR/simulated_helper.log" >&2 || true
echo "--- webserver.log (tail) ---" >&2
test -f "$ART_DIR/webserver.log" && tail -n 200 "$ART_DIR/webserver.log" >&2 || true

echo "--- ss -ltn (listening tcp ports) ---" >&2
ss -ltn || true

exit 1
