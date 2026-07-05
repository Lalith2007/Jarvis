#!/bin/bash
pkill -9 -f "J.A.R.V.I.S" || true
pkill -9 -f "jarvis-wake-listener" || true
echo "" > ~/Library/Logs/JARVIS/runtime.log
sleep 1
open dist/mac-arm64/J.A.R.V.I.S.app
sleep 15

echo "Starting 20-cycle loop"
for i in {1..20}; do
  echo "--- Cycle $i ---"
  say "Hey Jarvis"
  # Wait for wake to trigger, dashboard to show, and app to sleep, and cooldown to clear
  sleep 12
done

echo "Loop finished"
sleep 2
pkill -9 -f "J.A.R.V.I.S" || true
pkill -9 -f "jarvis-wake-listener" || true

echo "=== RESULTS ==="
echo "Total wakes:"
grep -c '"event":"wake"' ~/Library/Logs/JARVIS/runtime.log
echo "Total restartSoon() due to stale tasks (should be 0):"
grep -c "listener_stopped" ~/Library/Logs/JARVIS/runtime.log
echo "Total audio engine teardowns (should be 0):"
grep -c "audio_engine_stopped" ~/Library/Logs/JARVIS/runtime.log
echo "Total stale callbacks ignored:"
grep -c "recognition_task_finished_ignored" ~/Library/Logs/JARVIS/runtime.log
