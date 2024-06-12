import pandas as pd
import argparse
import numpy as np
import pathlib

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        args: An object containing the parsed arguments, with attributes 'i' (input file name), 's' (portfolio size), and 'csv' (export to CSV flag).
    """
    parser = argparse.ArgumentParser(description='Create a random portfolio of projects')
    parser.add_argument('-i', default='GHG_Test_Projects.xlsx', help='Input file name')
    parser.add_argument('-s', type=int, default=10, help='Portfolio size')
    parser.add_argument('-csv', action='store_true', help='Export portfolio to CSV file')

    args = parser.parse_args()

    if args.s <= 0:
        parser.error("Portfolio size must be a positive integer.")

    script_dir = pathlib.Path(__file__).parent
    file_path = script_dir / args.i
    if not file_path.exists():
        parser.error(f"Input file '{args.i}' does not exist.")

    return args

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from an Excel file.

    Args:
        file_path: The path to the Excel file.

    Returns:
        A dataframe containing the project data.
    """
    try:
        project_data = pd.read_excel(file_path, sheet_name='Project Data')
        return project_data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{file_path}' is empty.")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"Error parsing the file: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def generate_correlation_matrices(portfolio: pd.DataFrame) -> tuple:
    """
    Generate correlation matrices for the technologies and countries in the portfolio.

    Args:
        portfolio: A dataframe containing the portfolio data.

    Returns:
        A tuple of two dataframes. The first dataframe is the technology correlation matrix, and the second dataframe is the country correlation matrix.
    """
    try:
        technologies = portfolio['technology'].unique()
        countries = portfolio['country'].unique()

        num_technologies = len(technologies)
        technology_correlation_matrix = np.random.uniform(-1, 1, size=(num_technologies, num_technologies))
        technology_correlation_matrix = (technology_correlation_matrix + technology_correlation_matrix.T) / 2
        np.fill_diagonal(technology_correlation_matrix, 1)

        num_countries = len(countries)
        country_correlation_matrix = np.random.uniform(-1, 1, size=(num_countries, num_countries))
        country_correlation_matrix = (country_correlation_matrix + country_correlation_matrix.T) / 2
        np.fill_diagonal(country_correlation_matrix, 1)

        technology_correlation_matrix = pd.DataFrame(technology_correlation_matrix, index=technologies, columns=technologies)
        country_correlation_matrix = pd.DataFrame(country_correlation_matrix, index=countries, columns=countries)

        return technology_correlation_matrix, country_correlation_matrix
    except KeyError as e:
        print(f"Error accessing dataframe key: {e}")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(), pd.DataFrame()

def export_output(portfolio: pd.DataFrame, technology_correlation_matrix: pd.DataFrame, country_correlation_matrix: pd.DataFrame, export_csv: bool) -> None:
    """
    Export the portfolio data to a file.

    If export_csv is True, the portfolio is exported to a CSV file named 'GHG_Portfolio.csv' in the 'data' directory.
    Otherwise, the portfolio, technology correlation matrix, and country correlation matrix are exported to an Excel file named 'GHG_Portfolio_Data.xlsx' in the 'data' directory.

    Args:
        portfolio: A dataframe containing the portfolio data.
        technology_correlation_matrix: A dataframe containing the technology correlation matrix.
        country_correlation_matrix: A dataframe containing the country correlation matrix.
        export_csv: A boolean indicating whether to export the portfolio to a CSV file.
    """

    script_dir = pathlib.Path(__file__).parent
    data_dir = script_dir.parent / 'data'

    try:
        if export_csv:
            file_path = data_dir / 'GHG_Portfolio.csv'
            portfolio.to_csv(file_path, index=False)
        else:
            dataframes = {
                'Portfolio': portfolio,
                'Technology Correlation Matrix': technology_correlation_matrix,
                'Country Correlation Matrix': country_correlation_matrix,
            }

            file_path = data_dir / 'GHG_Portfolio_Data.xlsx'
            with pd.ExcelWriter(file_path) as writer:
                for worksheet_name, dataframe in dataframes.items():
                    if worksheet_name in ['Technology Correlation Matrix', 'Country Correlation Matrix']:
                        dataframe.to_excel(writer, sheet_name=worksheet_name, index=True)
                    else:
                        dataframe.to_excel(writer, sheet_name=worksheet_name, index=False)
    except FileNotFoundError as e:
        print(f"Error finding file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main() -> None:
    """
    The main function that calls all the other functions.
    """
    try:
        args = parse_args()

        script_dir = pathlib.Path(__file__).parent
        file_path = script_dir / args.i
        project_data = load_data(file_path)

        # Create a random portfolio of projects
        portfolio = project_data.sample(n=args.s, replace=False)

        # Generate correlation matrices for the portfolio
        technology_correlation_matrix, country_correlation_matrix = generate_correlation_matrices(portfolio)

        # Export the portfolio and correlation matrices to a file
        export_output(portfolio, technology_correlation_matrix, country_correlation_matrix, args.csv)

        print(f"Generated a portfolio of {args.s} projects with technology and country correlation matrices. Exported to {'CSV' if args.csv else 'Excel'}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()