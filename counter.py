import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def count_sum(seconds: int, delay: float = 1.0) -> int:
    total = 0
    for i in range(1, seconds + 1):
        total += i
        logging.info(f"Count: {i} | Current sum: {total}")
        if delay > 0:
            time.sleep(delay)
    return total

if __name__ == "__main__":
    logging.info("Starting Counter Application...")
    final_sum = count_sum(100, delay=1.0)
    logging.info(f"Final calculated sum: {final_sum}")