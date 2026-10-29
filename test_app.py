from counter import count_sum

def test_count_sum_five():
    assert count_sum(5, delay=0) == 15

def test_count_sum_hundred():
    assert count_sum(100, delay=0) == 5050