from counter import count_sum

def test_count_sum():
    # Testet die Logik für 5 Sekunden (1 + 2 + 3 + 4 + 5 = 15)
    assert count_sum(5) == 15