import unittest
import unittest.mock as mock
import logging
import pandas as pd
from utils.risk_calc import *

class TestCreateYearlyPortfolio(unittest.TestCase):
    def setUp(self):
        # Disable logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Enable logging
        logging.disable(logging.NOTSET)

    def test_empty_input(self):
        # Test with an empty input DataFrame
        empty_df = pd.DataFrame()
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = create_yearly_portfolio(empty_df)
            self.assertIsNone(result)

    def test_missing_columns(self):
        # Test with a DataFrame that's missing required columns
        df = pd.DataFrame({'project_id': [1], 'project_name': ['Test']})
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = create_yearly_portfolio(df)
            self.assertIsNone(result)

    def test_valid_input(self):
        # Test with a valid input DataFrame
        df = pd.DataFrame({
            'project_id': [1],
            'project_name': ['Test'],
            'contract_duration': [2],
            'country': ['USA'],
            'technology': ['Solar'],
            'counterparty': ['Company'],
            'start_year': [2020],
            'screening_date': ['2020-01-01'],
            'overall_project_rating': ['A'],
            'offered_volume_year_1': [100],
            'offered_volume_year_2': [200]
        })
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = create_yearly_portfolio(df)
            self.assertIsNotNone(result)

class TestBuildProjectCorrelationMatrix(unittest.TestCase):
    def setUp(self):
        # Disable logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Enable logging
        logging.disable(logging.NOTSET)

    def test_empty_input(self):
        # Test with empty input DataFrames
        empty_df = pd.DataFrame()
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = build_project_correlation_matrix(empty_df, empty_df, empty_df)
            self.assertIsNone(result)

    def test_missing_columns(self):
        # Test with DataFrames that are missing required columns
        df = pd.DataFrame({'project_id': [1], 'project_name': ['Test']})
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = build_project_correlation_matrix(df, df, df)
            self.assertIsNone(result)

    def test_valid_input(self):
        # Test with valid input DataFrames
        yearly_portfolio_df = pd.DataFrame({
            'project_name': ['Project 1', 'Project 2'],
            'technology': ['Solar', 'Wind'],
            'country': ['USA', 'Canada']
        })
        technology_correlation_matrix_df = pd.DataFrame({
            'Unnamed: 0': ['Solar', 'Wind'],
            'Solar': [1, 0.5],
            'Wind': [0.5, 1]
        })
        country_correlation_matrix_df = pd.DataFrame({
            'Unnamed: 0': ['USA', 'Canada'],
            'USA': [1, 0.7],
            'Canada': [0.7, 1]
        })
        with mock.patch('sys.stdout', new=mock.Mock()):
            result = build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, np.ndarray)

class TestRunPortfolioSimulation(unittest.TestCase):

    def setUp(self):
        # Disable logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Enable logging
        logging.disable(logging.NOTSET)

    def test_empty_input(self):
        # Test with an empty input DataFrame
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            run_portfolio_simulation(empty_df, [], 1000)

    def test_invalid_correlation_matrix(self):
        # Test with an invalid correlation matrix
        df = pd.DataFrame({
            'project_name': ['Project 1', 'Project 2'],
            'start_year': [2020, 2020],
            'contract_duration': [2, 2],
            'delivery_volume_2020': [100, 200],
            'standard_deviation_2020': [10, 20],
            'offered_volume_2020': [150, 250]
        })
        with self.assertRaises(ValueError):
            run_portfolio_simulation(df, 'invalid', 1000)

    def test_invalid_num_simulations(self):
        # Test with an invalid number of simulations
        df = pd.DataFrame({
            'project_name': ['Project 1', 'Project 2'],
            'start_year': [2020, 2020],
            'contract_duration': [2, 2],
            'delivery_volume_2020': [100, 200],
            'standard_deviation_2020': [10, 20],
            'offered_volume_2020': [150, 250]
        })
        with self.assertRaises(ValueError):
            run_portfolio_simulation(df, [[1, 0.5], [0.5, 1]], 'invalid')

    def test_valid_input(self):
        # Test with valid input
        df = pd.DataFrame({
            'project_name': ['Project 1', 'Project 2'],
            'start_year': [2020, 2020],
            'contract_duration': [2, 2],
            'delivery_volume_2020': [100, 200],
            'standard_deviation_2020': [10, 20],
            'offered_volume_2020': [150, 250],
            'delivery_volume_2021': [150, 250],
            'standard_deviation_2021': [15, 25],
            'offered_volume_2021': [200, 300]
        })
        result = run_portfolio_simulation(df, [[1, 0.5], [0.5, 1]], 1000)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()

        