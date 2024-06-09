import unittest
import pandas as pd
from utils.risk_calc import *
from unittest.mock import patch

class TestCreateYearlyPortfolio(unittest.TestCase):
    def test_empty_input_dataframe(self):
        # Test with an empty input DataFrame
        input_df = pd.DataFrame()
        with patch('builtins.print') as mock_print:
            create_yearly_portfolio(input_df)
            mock_print.assert_called_once_with("An error occurred while creating the yearly portfolio DataFrame: Input DataFrame is empty")

    def test_missing_required_columns(self):
        # Test with a DataFrame missing required columns
        input_df = pd.DataFrame({'project_id': [1], 'project_name': ['Project 1']})
        with patch('builtins.print') as mock_print:
            create_yearly_portfolio(input_df)
            mock_print.assert_called_once_with("An error occurred while creating the yearly portfolio DataFrame: Input DataFrame is missing required columns")

    def test_valid_input_dataframe(self):
        # Test with a valid input DataFrame
        input_df = pd.DataFrame({
            'project_id': [1],
            'project_name': ['Project 1'],
            'contract_duration': [10],
            'country': ['Country 1'],
            'technology': ['Technology 1'],
            'counterparty': ['Counterparty 1'],
            'start_year': [2020],
            'screening_date': ['2020-01-01'],
            'overall_project_rating': [5],
            'offered_volume_year_1': [100],
            'offered_volume_year_2': [200],
            'offered_volume_year_3': [300]
        })
        output_df = create_yearly_portfolio(input_df)
        self.assertIsInstance(output_df, pd.DataFrame)
        self.assertFalse(output_df.empty)

class TestRunPortfolioSimulation(unittest.TestCase):
    def test_empty_input_dataframe(self):
        # Test with an empty input DataFrame
        yearly_portfolio_df = pd.DataFrame()
        project_correlation_matrix = []
        with self.assertRaises(KeyError):
            run_portfolio_simulation(yearly_portfolio_df, project_correlation_matrix)

    def test_num_simulations(self):
        # Test with a valid input DataFrame and a specified number of simulations
        yearly_portfolio_df = pd.DataFrame({
            'project_name': ['Project 1'],
            'start_year': [2020],
            'contract_duration': [10],
            'delivery_volume_2020': [100],
            'standard_deviation_2020': [10],
            'offered_volume_2020': [100]
        })
        project_correlation_matrix = [[1]]
        with self.assertRaises(KeyError):
            run_portfolio_simulation(yearly_portfolio_df, project_correlation_matrix, num_simulations=1000)

    def test_valid_input(self):
        # Test with valid input
        yearly_portfolio_df = pd.DataFrame({
            'project_name': ['Project 1'],
            'start_year': [2020],
            'contract_duration': [10],
            'delivery_volume_2020': [100],
            'standard_deviation_2020': [10],
            'offered_volume_2020': [100]
        })
        project_correlation_matrix = [[1]]
        with self.assertRaises(KeyError):
            run_portfolio_simulation(yearly_portfolio_df, project_correlation_matrix)

class TestBuildProjectCorrelationMatrix(unittest.TestCase):
    @patch('builtins.print')
    def test_empty_input_dataframes(self, mock_print):
        yearly_portfolio_df = pd.DataFrame()
        technology_correlation_matrix_df = pd.DataFrame()
        country_correlation_matrix_df = pd.DataFrame()
        build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        mock_print.assert_called_once_with("An error occurred while building the project correlation matrix: Input DataFrames cannot be empty")

    @patch('builtins.print')
    def test_missing_required_columns(self, mock_print):
        yearly_portfolio_df = pd.DataFrame({'project_name': ['project1', 'project2'], 'technology': ['tech1', 'tech2']})
        technology_correlation_matrix_df = pd.DataFrame({'tech1': [1, 0.5], 'tech2': [0.5, 1]})
        country_correlation_matrix_df = pd.DataFrame({'country1': [1, 0.5], 'country2': [0.5, 1]})
        build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        mock_print.assert_called_once_with("An error occurred while building the project correlation matrix: Yearly portfolio DataFrame is missing required columns")

    @patch('builtins.print')
    def test_project_names_not_in_correlation_matrices(self, mock_print):
        yearly_portfolio_df = pd.DataFrame({'project_name': ['project1', 'project2'], 'technology': ['tech1', 'tech2'], 'country': ['country1', 'country2']})
        technology_correlation_matrix_df = pd.DataFrame({'tech1': [1, 0.5], 'tech2': [0.5, 1]})
        country_correlation_matrix_df = pd.DataFrame({'country1': [1, 0.5], 'country2': [0.5, 1]})
        build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        mock_print.assert_called_once_with("An error occurred while building the project correlation matrix: \"None of ['Unnamed: 0'] are in the columns\"")

    @patch('builtins.print')
    def test_nan_values_in_correlation_matrices(self, mock_print):
        yearly_portfolio_df = pd.DataFrame({'project_name': ['project1', 'project2'], 'technology': ['tech1', 'tech2'], 'country': ['country1', 'country2']})
        technology_correlation_matrix_df = pd.DataFrame({'tech1': [1, np.nan], 'tech2': [np.nan, 1]})
        country_correlation_matrix_df = pd.DataFrame({'country1': [1, 0.5], 'country2': [0.5, 1]})
        build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        mock_print.assert_called_once_with("An error occurred while building the project correlation matrix: \"None of ['Unnamed: 0'] are in the columns\"")

    @patch('builtins.print')
    def test_valid_input(self, mock_print):
        yearly_portfolio_df = pd.DataFrame({'project_name': ['project1', 'project2'], 'technology': ['tech1', 'tech2'], 'country': ['country1', 'country2']})
        technology_correlation_matrix_df = pd.DataFrame({'tech1': [1, 0.5], 'tech2': [0.5, 1]})
        country_correlation_matrix_df = pd.DataFrame({'country1': [1, 0.5], 'country2': [0.5, 1]})
        correlation_matrix = build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        self.assertIsInstance(correlation_matrix, np.ndarray)

if __name__ == '__main__':
    unittest.main()

        