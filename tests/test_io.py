import unittest
from unittest.mock import patch
from pathlib import Path
import pandas as pd
from utils.io import *

class TestLoadExcelData(unittest.TestCase):
    @patch('pandas.read_excel')
    def test_load_excel_data_valid(self, mock_read_excel):
        # Mock the excel file data
        mock_read_excel.return_value = {
            'Portfolio': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            'Technology Correlation Matrix': pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]}),
            'Country Correlation Matrix': pd.DataFrame({'col1': [9, 10], 'col2': [11, 12]}),
            'Default Rates': pd.DataFrame({'col1': [13, 14], 'col2': [15, 16]}),
            'Recovery Potential': pd.DataFrame({'col1': [17, 18], 'col2': [19, 20]}),
            'Model Config': pd.DataFrame({'col1': [21, 22], 'col2': [23, 24]})
        }

        # Mock the file existence
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True

            # Call the function
            result = load_excel_data(Path('test.xlsx'))

            # Check if the result is a tuple of DataFrames
            self.assertIsInstance(result, tuple)
            for df in result:
                self.assertIsInstance(df, pd.DataFrame)

    @patch('pandas.read_excel')
    def test_load_excel_data_invalid_missing_sheet(self, mock_read_excel):
        # Mock the excel file data with a missing sheet
        mock_read_excel.return_value = {
            'Portfolio': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            'Technology Correlation Matrix': pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]}),
            'Country Correlation Matrix': pd.DataFrame({'col1': [9, 10], 'col2': [11, 12]}),
            'Default Rates': pd.DataFrame({'col1': [13, 14], 'col2': [15, 16]}),
            'Recovery Potential': pd.DataFrame({'col1': [17, 18], 'col2': [19, 20]})
        }

        # Mock the file existence
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True

            # Call the function
            with self.assertRaises(ValueError):
                load_excel_data(Path('test.xlsx'))

    @patch('pandas.read_excel')
    def test_load_excel_data_invalid_empty_dataframe(self, mock_read_excel):
        # Mock the excel file data with an empty DataFrame
        mock_read_excel.return_value = {
            'Portfolio': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            'Technology Correlation Matrix': pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]}),
            'Country Correlation Matrix': pd.DataFrame({'col1': [9, 10], 'col2': [11, 12]}),
            'Default Rates': pd.DataFrame({'col1': [13, 14], 'col2': [15, 16]}),
            'Recovery Potential': pd.DataFrame({'col1': [17, 18], 'col2': [19, 20]}),
            'Model Config': pd.DataFrame()
        }

        # Mock the file existence
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True

            # Call the function
            with self.assertRaises(ValueError):
                load_excel_data(Path('test.xlsx'))

    def test_load_excel_data_invalid_file_not_found(self):
        # Mock the file existence
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False

            # Call the function
            with self.assertRaises(FileNotFoundError):
                load_excel_data(Path('test.xlsx'))

class TestPrintAndExportSimulationResults(unittest.TestCase):
    @patch('builtins.print')
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.ExcelWriter')
    def test_print_and_export_simulation_results(self, mock_excel_writer, mock_to_excel, mock_print):
        # Mock the results
        results = [(2022, 0.5, 50.0, 10.0, 0.5), (2023, 0.6, 60.0, 12.0, 0.6)]
        yearly_portfolio_df = pd.DataFrame({'Year': [2022, 2023], 'Project': ['Project A', 'Project B']})

        # Call the function
        print_and_export_simulation_results(results, Path('output_dir'), '2022-01-01 12:00:00', yearly_portfolio_df)

        # Check if the ExcelWriter was called correctly
        mock_excel_writer.assert_called_once_with(Path('output_dir') / 'Portfolio_Simulation_Results.xlsx', engine='xlsxwriter')

        # Check if the to_excel method was called twice (once for each worksheet)
        self.assertEqual(mock_to_excel.call_count, 2)

    @patch('builtins.print')
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.ExcelWriter')
    def test_print_and_export_simulation_results_empty_results(self, mock_excel_writer, mock_to_excel, mock_print):
        # Mock the results
        results = []
        yearly_portfolio_df = pd.DataFrame({'Year': [], 'Project': []})

        # Call the function
        print_and_export_simulation_results(results, Path('output_dir'), '2022-01-01 12:00:00', yearly_portfolio_df)

        # Check if the ExcelWriter was called correctly
        mock_excel_writer.assert_called_once_with(Path('output_dir') / 'Portfolio_Simulation_Results.xlsx', engine='xlsxwriter')

        # Check if the to_excel method was called twice (once for each worksheet)
        self.assertEqual(mock_to_excel.call_count, 2)

class TestExportModelConfiguration(unittest.TestCase): 
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.ExcelWriter')
    def test_valid_export_model_configuration(self, mock_excel_writer, mock_to_excel):
        default_rates_df = pd.DataFrame({'Default Rates': [1, 2, 3]})
        recovery_potential_df = pd.DataFrame({'Recovery Potential': [4, 5, 6]})
        model_config_df = pd.DataFrame({'Model Config': [7, 8, 9]})
        output_dir = Path('output_dir')
        
        export_model_configuration(default_rates_df, recovery_potential_df, model_config_df, output_dir)
        
        mock_excel_writer.assert_called_once_with(output_dir / 'Model_Configuration.xlsx')
        self.assertEqual(mock_to_excel.call_count, 3)
        
    @patch('builtins.print')
    @patch('pandas.ExcelWriter')
    def test_invalid_export_model_configuration(self, mock_excel_writer, mock_print):
        default_rates_df = pd.DataFrame({'Default Rates': [1, 2, 3]})
        recovery_potential_df = pd.DataFrame({'Recovery Potential': [4, 5, 6]})
        model_config_df = pd.DataFrame({'Model Config': [7, 8, 9]})
        output_dir = Path('output_dir')
        
        mock_excel_writer.side_effect = Exception('Mocked exception')
        
        export_model_configuration(default_rates_df, recovery_potential_df, model_config_df, output_dir)
        
        mock_excel_writer.assert_called_once_with(output_dir / 'Model_Configuration.xlsx')
        mock_print.assert_called_once_with('An error occurred while writing to the Excel file: Mocked exception')

if __name__ == '__main__':
    unittest.main()
