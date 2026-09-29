import time
import sys

for i in range(10):
    print(f"Count: {i}", flush=True)
    time.sleep(1)

print("Task ended.", flush=True)
sys.exit(0)