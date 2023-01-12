from unittest import TestCase
from main import FinData

class TestFinData(TestCase):
    fin_data_test_subject = None
    def __init__(self):
        self.fin_data_test_subject = FinData()
    def test_get_revenue(self):
        self.fail()
