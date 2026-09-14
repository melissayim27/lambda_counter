import time
import sys

print("Task started...")
for i in range(1001):
    print(f"Count: {i}", flush=True)
    time.sleep(1)

print("Task ended.")