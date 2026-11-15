# usage: driver.sh <jobs-file>   runs jobs sequentially, skipping ones already DONE
cd /scratch/cc-pr43
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if [ "${line%%|*}" = "cmd" ]; then
    rest=${line#cmd|}; name=${rest%%|*}; cmd=${rest#*|}
    grep -q DONE logs/$name/job.status 2>/dev/null && continue
    mkdir -p logs/$name
    echo "$(date -u +%H:%M:%S) start $name" >> logs/driver.log
    bash -c "$cmd" > logs/$name/cmd.log 2>&1 < /dev/null
    echo "cmd rc=$?" > logs/$name/job.status; echo DONE >> logs/$name/job.status
    echo "$(date -u +%H:%M:%S) end $name: $(tr '\n' ';' < logs/$name/job.status)" >> logs/driver.log
    continue
  fi
  name=${line%%|*}
  grep -q DONE logs/$name/job.status 2>/dev/null && continue
  echo "$(date -u +%H:%M:%S) start $name" >> logs/driver.log
  bash box/job.sh "$line"
  echo "$(date -u +%H:%M:%S) end $name: $(tr '\n' ';' < logs/$name/job.status)" >> logs/driver.log
done < "$1"
echo "$(date -u +%H:%M:%S) DRIVER_DONE $1" >> logs/driver.log
