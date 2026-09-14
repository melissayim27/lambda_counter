import time
import sys

print("Task started...")
for i in range(10):
    print(f"Count: {i}", flush=True)
    time.sleep(1)

print("Task ended.")