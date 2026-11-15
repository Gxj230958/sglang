tmux kill-session -t ccpr43 2>/dev/null
sleep 2
MAIN=$(pgrep -f "sglang.launch_server.*--port 31743" || true)
ALL="$MAIN"
for p in $MAIN; do ALL="$ALL $(pgrep -P $p | tr '\n' ' ')"; done
[ -n "$(echo $ALL)" ] && kill -9 $ALL 2>/dev/null
sleep 6
nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' '
