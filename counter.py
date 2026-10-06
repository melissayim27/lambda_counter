import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def count_sum(seconds: int) -> int:
    """Zählt x Sekunden lang und berechnet die Summe (1 + 2 + ... + x)."""
    total = 0
    for i in range(1, seconds + 1):
        total += i
        logging.info(f"Second {i}: Current sum = {total}")
        time.sleep(1)
    return total

if __name__ == "__main__":
    logging.info("Starting Counter Application...")
    final_sum = count_sum(5)  # Beispiel: 5 Sekunden
    logging.info(f"Final calculated sum: {final_sum}")