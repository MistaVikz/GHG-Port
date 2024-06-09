import pandas as pd
import numpy as np

def validate_yearly_portfolio(yearly_portfolio_df: pd.DataFrame) -> bool:
    """
    Validate the yearly portfolio DataFrame.
    
    This function checks if the yearly portfolio is not empty, if the project ids are unique,
    and if the calendar years are within the range of 2000 to 2100.
    
    Parameters:
    yearly_portfolio_df (pd.DataFrame): The yearly portfolio DataFrame.
    
    Returns:
    bool: True if the yearly portfolio is valid, False otherwise.
    """
    
    # Check if the yearly portfolio is not empty
    if yearly_portfolio_df.empty:
        print("Error: The yearly portfolio is empty")
        return False
    
    # Check if the project ids are unique
    if yearly_portfolio_df['project_id'].duplicated().any():
        print("Error: The yearly portfolio contains duplicate project ids")
        return False
    
    # Check if the calendar years are within the range of 2000 to 2100
    calendar_years = [int(col.split('_')[-1]) for col in yearly_portfolio_df.columns if col not in ['project_id', 'project_name', 'contract_duration', 'country', 'technology', 'counterparty', 'start_year', 'screening_date', 'overall_project_rating']]
    if not all(2000 <= year <= 2100 for year in calendar_years):
        print("Error: The yearly portfolio contains calendar years outside the range of 2000 to 2100")
        return False
    
    return True

def validate_project_correlation_matrix(correlation_matrix: np.ndarray) -> bool:
    """
    Validate the project correlation matrix.

    Args:
    correlation_matrix (np.ndarray): The project correlation matrix.

    Returns:
    bool: True if the correlation matrix is valid, False otherwise.
    """

    # Check if the correlation matrix only contains numeric values
    if not np.issubdtype(correlation_matrix.dtype, np.number):
        print("Error: The project correlation matrix must only contain numeric values")
        return False

    # Check if the correlation matrix is symmetric
    if not np.allclose(correlation_matrix, correlation_matrix.T):
        print("Error: The project correlation matrix is not symmetric")
        return False

    # Check if the correlation matrix contains NaN values
    if np.isnan(correlation_matrix).any():
        print("Error: The project correlation matrix contains NaN values")
        return False

    # Check if the correlation matrix is positive semi-definite
    eigenvalues = np.linalg.eigvals(correlation_matrix)
    if not np.all(eigenvalues >= 0):
        print("Error: The project correlation matrix is not positive semi-definite")
        return False

    return True
    
def validate_simulation_results(results: list) -> bool:
    """
    Validate the results of the portfolio simulation.

    Args:
    results (list): A list of tuples, each containing the year, overall standard deviation, overall portfolio delivery, and overall delivery rate.

    Returns:
    bool: True if the simulation results are valid, False otherwise.
    """

    # Check if the results list is empty
    if not results:
        print("Error: The portfolio simulation results are empty")
        return False

    # Check if the standard deviations are non-negative
    std_devs = [result[1] for result in results]

    if any(std_dev < 0 for std_dev in std_devs):
        print("Error: The standard deviations in the portfolio simulation results must be non-negative")
        return False

    # Check if the overall portfolio deliveries are non-negative
    portfolio_deliveries = [result[2] for result in results]

    if any(delivery < 0 for delivery in portfolio_deliveries):
        print("Error: The overall portfolio deliveries in the portfolio simulation results must be non-negative")
        return False

    # Check if the overall delivery rates are between 0 and 1
    delivery_rates = [result[3] for result in results]

    if any(rate < 0 or rate > 1 for rate in delivery_rates):
        print("Error: The overall delivery rates in the portfolio simulation results must be between 0 and 1")
        return False
    
    return True