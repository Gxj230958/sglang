cd /scratch/cc-pr43
until grep -q "DRIVER_DONE box/jobs1.txt" logs/driver.log 2>/dev/null; do sleep 20; done
bash box/driver.sh box/jobs2.txt
