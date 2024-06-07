import unittest
from unittest.mock import patch
import pandas as pd
import os
from utils.validation import *

class TestValidateYearlyPortfolio(unittest.TestCase):
    def setUp(self):
        self.yearly_portfolio_df = pd.DataFrame({
            'project_id': [1, 2, 3],
            'project_name': ['Project 1', 'Project 2', 'Project 3'],
            '2020': [100, 200, 300],
            '2021': [400, 500, 600],
            '2022': [700, 800, 900]
        })

    @patch('sys.stdout')
    def test_empty_dataframe(self, mock_stdout):
        empty_df = pd.DataFrame()
        self.assertFalse(validate_yearly_portfolio(empty_df))

    @patch('sys.stdout')
    def test_duplicate_project_ids(self, mock_stdout):
        duplicate_df = pd.DataFrame({
            'project_id': [1, 1, 3],
            'project_name': ['Project 1', 'Project 2', 'Project 3'],
            '2020': [100, 200, 300],
            '2021': [400, 500, 600],
            '2022': [700, 800, 900]
        })
        self.assertFalse(validate_yearly_portfolio(duplicate_df))

    @patch('sys.stdout')
    def test_invalid_calendar_year(self, mock_stdout):
        invalid_year_df = pd.DataFrame({
            'project_id': [1, 2, 3],
            'project_name': ['Project 1', 'Project 2', 'Project 3'],
            '1999': [100, 200, 300],
            '2021': [400, 500, 600],
            '2022': [700, 800, 900]
        })
        self.assertFalse(validate_yearly_portfolio(invalid_year_df))

    @patch('sys.stdout', open(os.devnull, 'w'))
    def test_valid_dataframe(self):
        self.assertTrue(validate_yearly_portfolio(self.yearly_portfolio_df))

class TestValidateProjectCorrelationMatrix(unittest.TestCase):
    @patch('sys.stdout')
    def test_non_numeric_correlation_matrix(self, mock_stdout):
        non_numeric_matrix = np.array([[1, 2, 'a'], [4, 5, 6], [7, 8, 9]])
        self.assertFalse(validate_project_correlation_matrix(non_numeric_matrix))

    @patch('sys.stdout')
    def test_asymmetric_correlation_matrix(self, mock_stdout):
        asymmetric_matrix = np.array([[1, 0.5, 0.2], [0.3, 1, 0.7], [0.2, 0.5, 1]])
        self.assertFalse(validate_project_correlation_matrix(asymmetric_matrix))

    @patch('sys.stdout')
    def test_correlation_matrix_with_non_unit_diagonal(self, mock_stdout):
        non_unit_diagonal_matrix = np.array([[1.1, 0.5, 0.2], [0.5, 1, 0.7], [0.2, 0.7, 1]])
        self.assertFalse(validate_project_correlation_matrix(non_unit_diagonal_matrix))

    @patch('sys.stdout')
    def test_valid_correlation_matrix(self, mock_stdout):
        valid_matrix = np.array([[1, 0.5, 0.2], [0.5, 1, 0.7], [0.2, 0.7, 1]])
        self.assertTrue(validate_project_correlation_matrix(valid_matrix))

class TestValidateSimulationResults(unittest.TestCase):
    @patch('sys.stdout')
    def test_empty_results(self, mock_stdout):
        empty_results = []
        self.assertFalse(validate_simulation_results(empty_results))

    @patch('sys.stdout')
    def test_negative_std_dev(self, mock_stdout):
        results_with_negative_std_dev = [(2020, -1, 100, 0.5), (2021, 2, 200, 0.7)]
        self.assertFalse(validate_simulation_results(results_with_negative_std_dev))

    @patch('sys.stdout')
    def test_negative_portfolio_delivery(self, mock_stdout):
        results_with_negative_portfolio_delivery = [(2020, 1, -100, 0.5), (2021, 2, 200, 0.7)]
        self.assertFalse(validate_simulation_results(results_with_negative_portfolio_delivery))

    @patch('sys.stdout')
    def test_invalid_delivery_rate(self, mock_stdout):
        results_with_invalid_delivery_rate = [(2020, 1, 100, -0.5), (2021, 2, 200, 1.7)]
        self.assertFalse(validate_simulation_results(results_with_invalid_delivery_rate))

    @patch('sys.stdout')
    def test_valid_results(self, mock_stdout):
        valid_results = [(2020, 1, 100, 0.5), (2021, 2, 200, 0.7)]
        self.assertTrue(validate_simulation_results(valid_results))

if __name__ == '__main__':
    unittest.main()