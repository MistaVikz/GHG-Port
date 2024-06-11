import argparse
from pathlib import Path
from datetime import datetime
from utils.io import *
from utils.risk_calc import *
from utils.validation import *
import logging

def main(file_path: Path) -> None:
    """
    Creates a yearly portfolio and correlation matrix.

    Args:
    file_path (Path): The path to the Excel file containing the portfolio data.

    Returns:
    None
    """
    logging.basicConfig(level=logging.ERROR)

    try:
        # Load the Excel data
        portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df, default_rates_df, recovery_potential_df, model_config_df = load_excel_data(file_path)

        # Build the yearly portfolio
        yearly_portfolio_df = create_yearly_portfolio(portfolio_df)
        if not validate_yearly_portfolio(yearly_portfolio_df):
            return
        
        # Build the project correlation matrix
        project_correlation_matrix = build_project_correlation_matrix(yearly_portfolio_df, technology_correlation_matrix_df, country_correlation_matrix_df)
        if not validate_project_correlation_matrix(project_correlation_matrix):
            return

        # Run the portfolio simulation
        simulation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = run_portfolio_simulation(yearly_portfolio_df, project_correlation_matrix)
        if not validate_simulation_results(results):
            return
        
        # Create a timestamped directory in the /output sub directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path('output') / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export the results and configuration to excel
        print_and_export_simulation_results(results, output_dir, simulation_date, yearly_portfolio_df)
        export_model_configuration(default_rates_df, recovery_potential_df, model_config_df, output_dir)

    except Exception as e:
        logging.error("An error occurred", exc_info=e)
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='GHG_Portfolio_Data.xlsx', help='The name of the Excel file containing the portfolio data')
    args = parser.parse_args()
    file_path = Path('data') / args.input
    main(file_path)