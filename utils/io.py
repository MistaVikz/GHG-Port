import pandas as pd
from pathlib import Path
from tabulate import tabulate

def load_excel_data(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load Excel data from a file, perform data preparation, and return a tuple of DataFrames.

    This function loads an Excel file into a dictionary of DataFrames, checks if all required sheets exist, 
    checks if all DataFrames are not empty, and drops columns with 'risk_bucket' in their name from the 
    'Portfolio' DataFrame.

    Args:
        file_path (Path): The path to the Excel file.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
            A tuple containing the following DataFrames:
                1. Portfolio
                2. Technology Correlation Matrix
                3. Country Correlation Matrix
                4. Default Rates
                5. Recovery Potential
                6. Model Config

    Raises:
        FileNotFoundError: If the file at file_path does not exist.
        ValueError: If the Excel file is missing required sheets or if any of the DataFrames are empty.
    """
    
    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist")
    
    sheets = pd.read_excel(file_path, sheet_name=None)
    
    # Check if all required sheets exist
    required_sheets = ['Portfolio', 'Technology Correlation Matrix', 'Country Correlation Matrix', 'Default Rates', 'Recovery Potential', 'Model Config']
    if not all(sheet in sheets for sheet in required_sheets):
        raise ValueError("The Excel file is missing required sheets")
    
    # Load DataFrames
    dataframes = {
        'portfolio': sheets['Portfolio'],
        'technology_correlation_matrix': sheets['Technology Correlation Matrix'],
        'country_correlation_matrix': sheets['Country Correlation Matrix'],
        'default_rates': sheets['Default Rates'],
        'recovery_potential': sheets['Recovery Potential'],
        'model_config': sheets['Model Config'],
    }
    
    # Check if DataFrames are not empty
    for name, df in dataframes.items():
        if df.empty:
            raise ValueError(f"The '{name}' DataFrame is empty")
    
    # Drop columns with 'risk_bucket' in their name from the 'Portfolio' DataFrame
    dataframes['portfolio'] = dataframes['portfolio'].drop(columns=[col for col in dataframes['portfolio'].columns if 'risk_bucket' in col.lower()])
    
    return tuple(dataframes.values())

def print_and_export_simulation_results(results: list[tuple[int, float, float, float, float]], output_dir: Path, simulation_date: str) -> None:
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
    except Exception as e:
        print(f"An error occurred while writing to the Excel file: {e}")

def export_model_configuration(default_rates_df: pd.DataFrame, recovery_potential_df: pd.DataFrame, model_config_df: pd.DataFrame, output_dir: Path) -> None:
    """
    Exports the model configuration dataframes to Excel.

    Args:
    default_rates_df (pd.DataFrame): The default rates dataframe.
    recovery_potential_df (pd.DataFrame): The recovery potential dataframe.
    model_config_df (pd.DataFrame): The model configuration dataframe.
    output_dir (Path): The output directory.

    Returns:
    None
    """
    
    try:
        with pd.ExcelWriter(output_dir / 'Model_Configuration.xlsx') as writer:
            model_config_df.to_excel(writer, sheet_name='Model Config', index=False)
            default_rates_df.to_excel(writer, sheet_name='Default Rates', index=False)
            recovery_potential_df.to_excel(writer, sheet_name='Recovery Potential', index=False)
            
            # Adjust column widths
            for worksheet in writer.sheets.values():
                worksheet.set_column(0, 0, 23)
                if worksheet.get_name() == 'Model Config':
                    worksheet.set_column(1, model_config_df.shape[1], 23)
    except Exception as e:
        print(f"An error occurred while writing to the Excel file: {e}")