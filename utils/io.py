import pandas as pd
import logging
from pathlib import Path
from tabulate import tabulate

def load_excel_data(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load Excel data from a file, perform data preparation, and return a tuple of DataFrames.

    This function loads an Excel file into a dictionary of DataFrames, checks if all required sheets exist, 
    checks if all DataFrames are not empty, and drops columns with 'risk_bucket' in their name from the 
    'Portfolio' DataFrame.

    Args:
        file_path (Path): The path to the Excel file.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
            A tuple containing the following DataFrames:
                1. Portfolio
                2. Technology Correlation Matrix
                3. Country Correlation Matrix

    Raises:
        FileExistsError: If the file at file_path does not exist.
        ValueError: If the Excel file is missing required sheets or if any of the DataFrames are empty.
    """
    
    # Define the required sheets
    required_sheets = ['Portfolio', 'Technology Correlation Matrix', 'Country Correlation Matrix']
    
    # Check if the file exists
    if not file_path.exists():
        logging.error(f"The file {file_path} does not exist")
        raise FileExistsError(f"The file {file_path} does not exist")
    
    sheets = pd.read_excel(file_path, sheet_name=None)
    
    # Check if all required sheets exist
    if not all(sheet in sheets for sheet in required_sheets):
        missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
        logging.error(f"The Excel file is missing required sheets: {missing_sheets}")
        raise ValueError(f"The Excel file is missing required sheets: {missing_sheets}")
    
    # Load DataFrames
    dataframes = {
        'portfolio': sheets['Portfolio'],
        'technology_correlation_matrix': sheets['Technology Correlation Matrix'],
        'country_correlation_matrix': sheets['Country Correlation Matrix'],
    }
    
    # Check if DataFrames are not empty
    for name, df in dataframes.items():
        if df.empty:
            logging.error(f"The '{name}' DataFrame is empty")
            raise ValueError(f"The '{name}' DataFrame is empty")
    
    # Drop columns with 'risk_bucket' in their name from the 'Portfolio' DataFrame
    dataframes['portfolio'] = dataframes['portfolio'].drop(columns=[col for col in dataframes['portfolio'].columns if 'risk_bucket' in col.lower()])
    
    return tuple(dataframes.values())

def print_and_export_simulation_results(results: list[tuple[int, float, float, float, float]], output_dir: Path, simulation_date: str, yearly_portfolio_df: pd.DataFrame) -> None:
    """
    Prints and exports the results of a portfolio simulation.

    Args:
        results (list[tuple[int, float, float, float, float]]): A list of tuples, each containing the year, offered volume, portfolio delivery, standard deviation, and delivery rate.
        output_dir (Path): The directory where the excel file will be saved.
        simulation_date (str): The date and time the simulation was run.

    Returns:
        None
    """
    
    # Create a table to display the results
    results_table = []
    portfolio_deliveries = []
    delivery_rates = []
    offered_volumes = []
    
    for year, standard_deviation, portfolio_delivery, delivery_rate, offered_volume in results:
        results_table.append([year, offered_volume, portfolio_delivery, standard_deviation, delivery_rate])
        portfolio_deliveries.append(portfolio_delivery)
        delivery_rates.append(delivery_rate)
        offered_volumes.append(offered_volume)

    # Calculate the summary statistics
    total_offered_volume = sum(offered_volumes)
    total_portfolio_delivery = sum(portfolio_deliveries)
    if delivery_rates:
        average_delivery_rate = sum(delivery_rates) / len(delivery_rates)
    else:
        average_delivery_rate = float('nan')  # or some other default value

    # Print the table
    print("Portfolio Simulation Results:")
    print(f"Simulation Date: {simulation_date}")
    print(tabulate([[year, f"{offered_volume:.2f}", f"{portfolio_delivery:.2f}", f"{standard_deviation:.2f}", f"{delivery_rate:.2f}"] for year, offered_volume, portfolio_delivery, standard_deviation, delivery_rate in results_table], headers=["Year", "Offered Volume", "Portfolio Delivery", "Standard Deviation", "Delivery Rate"], tablefmt="fancy_grid"))

    # Print the summary statistics
    print(f"Total Offered Volume: {total_offered_volume:.2f}")
    print(f"Total Portfolio Delivery: {total_portfolio_delivery:.2f}")
    print(f"Average Delivery Rate: {average_delivery_rate:.2f}")

    # Create a pandas DataFrame
    results_df = pd.DataFrame(results_table, columns=["Year", "Offered Volume", "Portfolio Delivery", "Standard Deviation", "Delivery Rate"])

    # Add the summary statistics to the DataFrame
    results_df.loc[len(results_df)] = ["", "", "", "", ""]
    results_df.loc[len(results_df)] = ["Total Offered Volume", total_offered_volume, "", "", ""]
    results_df.loc[len(results_df)] = ["Total Portfolio Delivery", total_portfolio_delivery, "", "", ""]
    results_df.loc[len(results_df)] = ["Average Delivery Rate", average_delivery_rate, "", "", ""]
    results_df.loc[len(results_df)] = ["", "", "", "", ""]
    results_df.loc[len(results_df)] = ["Simulation Date", simulation_date, "", "", ""]

    try:
        # Write the results to the worksheet
        with pd.ExcelWriter(output_dir / 'Portfolio_Simulation_Results.xlsx', engine='xlsxwriter') as writer:
            
            results_df.to_excel(writer, sheet_name="Simulation Results", index=False, startrow=2)
            worksheet = writer.book.worksheets()[0]

            for col in range(5):
                worksheet.set_column(col, col, 22)

            # Set the title
            title_format = writer.book.add_format({'bold': True, 'font_size': 14})
            worksheet.write(0, 0, "Portfolio Simulation Results", title_format)

            # Format the numeric columns
            num_format = writer.book.add_format({'num_format': '#,##0.00'})
            worksheet.set_column(1, 4, 22, num_format)

            # Bold the summary statistic labels
            bold = writer.book.add_format({'bold': True})
            for row in range(len(results_df) - 5, len(results_df) - 1):
                worksheet.write(row + 3, 0, results_df.iloc[row, 0], bold)  

            worksheet.write(len(results_df) + 2, 0, results_df.iloc[-1, 0], bold)

            # Export the yearly portfolio to a separate worksheet
            yearly_portfolio_df.to_excel(writer, sheet_name="Yearly Portfolio", index=False)
            worksheet = writer.book.worksheets()[1]

            for col in range(len(yearly_portfolio_df.columns)):
                worksheet.set_column(col, col, 22)

    except Exception as e:
        logging.error(f"An error occurred while writing to the Excel file: {e}")
        print(f"An error occurred while writing to the Excel file: {e}")
