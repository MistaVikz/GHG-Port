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

class TestValidateProjectCorrelationMatrix(unittest.TestCase):
    def test_numeric_matrix(self):
        correlation_matrix = np.array([[1, 0.5], [0.5, 1]])
        self.assertTrue(validate_project_correlation_matrix(correlation_matrix))

    def test_non_numeric_matrix(self):
        correlation_matrix = np.array([['a', 'b'], ['c', 'd']])
        with patch('builtins.print') as mock_print:
            self.assertFalse(validate_project_correlation_matrix(correlation_matrix))

    def test_symmetric_matrix(self):
        correlation_matrix = np.array([[1, 0.5], [0.5, 1]])
        self.assertTrue(validate_project_correlation_matrix(correlation_matrix))

    def test_non_symmetric_matrix(self):
        correlation_matrix = np.array([[1, 0.5], [0.6, 1]])
        with patch('builtins.print') as mock_print:
            self.assertFalse(validate_project_correlation_matrix(correlation_matrix))

    def test_nan_matrix(self):
        correlation_matrix = np.array([[1, np.nan], [np.nan, 1]])
        with patch('builtins.print') as mock_print:
            self.assertFalse(validate_project_correlation_matrix(correlation_matrix))

    def test_positive_semi_definite_matrix(self):
        correlation_matrix = np.array([[1, 0.5], [0.5, 1]])
        self.assertTrue(validate_project_correlation_matrix(correlation_matrix))

    def test_non_positive_semi_definite_matrix(self):
        correlation_matrix = np.array([[1, 2], [2, 1]])
        with patch('builtins.print') as mock_print:
            self.assertFalse(validate_project_correlation_matrix(correlation_matrix))
            
if __name__ == '__main__':
    unittest.main()