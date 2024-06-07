import pandas as pd
import numpy as np

def create_yearly_portfolio(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a yearly portfolio DataFrame from the portfolio DataFrame.
    
    This function melts the offered_volume_year_i columns into a single column,
    pivots the DataFrame to get the desired output, and reorders the columns
    so that similar columns are together.
    
    Parameters:
    portfolio_df (pd.DataFrame): The portfolio DataFrame.
    
    Returns:
    pd.DataFrame: The yearly portfolio DataFrame.
    """
    
    try:
        # Check if the input DataFrame is empty
        if portfolio_df.empty:
            raise ValueError("Input DataFrame is empty")
        
        # Check if the required columns exist
        required_columns = ['project_id', 'project_name', 'contract_duration', 'country', 'technology', 'counterparty', 'start_year', 'screening_date', 'overall_project_rating']
        if not all(col in portfolio_df.columns for col in required_columns):
            raise ValueError("Input DataFrame is missing required columns")
        
        # Melt the offered_volume_year_i columns into a single column
        yearly_portfolio_df = pd.melt(portfolio_df, id_vars=required_columns, 
                                       var_name='variable', value_name='value')
        
        # Extract the year index from the 'variable' column
        yearly_portfolio_df['year_index'] = yearly_portfolio_df['variable'].str.extract(r'year_(\d+)', expand=False)
        yearly_portfolio_df = yearly_portfolio_df.dropna(subset=['year_index'])
        yearly_portfolio_df['year_index'] = yearly_portfolio_df['year_index'].astype(int)
        
        # Calculate the calendar year
        yearly_portfolio_df['calendar_year'] = yearly_portfolio_df['start_year'] + yearly_portfolio_df['year_index'] - 1
        
        # Drop the 'year_index' column
        yearly_portfolio_df = yearly_portfolio_df.drop(columns=['year_index'])
        
        # Drop rows with missing values
        yearly_portfolio_df = yearly_portfolio_df.dropna(subset=['value'])
        
        # Extract the variable name from the 'variable' column
        yearly_portfolio_df['variable'] = yearly_portfolio_df['variable'].str.extract(r'project_(.+)_year', expand=False)
        yearly_portfolio_df['variable'] = yearly_portfolio_df['variable'].fillna('offered_volume')
        
        # Pivot the DataFrame to get the desired output
        yearly_portfolio_df = yearly_portfolio_df.pivot(index=['project_id', 'project_name', 'contract_duration', 'country', 'technology', 'counterparty', 'start_year', 'screening_date', 'overall_project_rating'], 
                                                        columns=['variable', 'calendar_year'], values='value')
        yearly_portfolio_df = yearly_portfolio_df.reset_index()
        
        # Reorder the columns
        variable_order = ['offered_volume', 'standard_deviation', 'delivery_volume', 'expected_value_percentage']
        calendar_years = sorted([int(year) for year in yearly_portfolio_df.columns.get_level_values(1).unique() if year != ''])
        ordered_columns = [('project_id', '')] + [('project_name', '')] + [('contract_duration', '')] + [('country', '')] + [('technology', '')] + [('counterparty', '')] + [('start_year', '')] + [('screening_date', '')] + [('overall_project_rating', '')] + [(var, year) for var in variable_order for year in calendar_years]
        yearly_portfolio_df = yearly_portfolio_df.reindex(columns=ordered_columns)
        yearly_portfolio_df.columns = [col[0] if isinstance(col, tuple) and col[1] == '' else '_'.join(str(x) for x in col).strip('_') for col in yearly_portfolio_df.columns]
        
        return yearly_portfolio_df
    except Exception as e:
        print(f"An error occurred while creating the yearly portfolio DataFrame: {e}")
        return pd.DataFrame()

def build_project_correlation_matrix(yearly_portfolio_df: pd.DataFrame, technology_correlation_matrix_df: pd.DataFrame, country_correlation_matrix_df: pd.DataFrame) -> np.ndarray:
    """
    Build the project correlation matrix.

    Args:
    yearly_portfolio_df (pd.DataFrame): The yearly portfolio DataFrame.
    technology_correlation_matrix_df (pd.DataFrame): The technology correlation matrix DataFrame.
    country_correlation_matrix_df (pd.DataFrame): The country correlation matrix DataFrame.

    Returns:
    np.ndarray: The project correlation matrix as a numpy array.
    """
    try:
        # Check if the input DataFrames are empty
        if yearly_portfolio_df.empty or technology_correlation_matrix_df.empty or country_correlation_matrix_df.empty:
            raise ValueError("Input DataFrames cannot be empty")

        # Check if the required columns exist in the DataFrames
        required_columns = ['project_name', 'technology', 'country']
        if not all(column in yearly_portfolio_df.columns for column in required_columns):
            raise ValueError("Yearly portfolio DataFrame is missing required columns")

        # Set the Unnamed: 0 column as the index of the technology correlation matrix
        technology_correlation_matrix_df.set_index('Unnamed: 0', inplace=True)
        country_correlation_matrix_df.set_index('Unnamed: 0', inplace=True)

        # Check if the project names, technologies, and countries in yearly_portfolio_df exist in the correlation matrices
        project_technologies = yearly_portfolio_df.set_index('project_name')['technology'].to_dict()
        project_countries = yearly_portfolio_df.set_index('project_name')['country'].to_dict()
        for technology in project_technologies.values():
            if technology not in technology_correlation_matrix_df.index or technology not in technology_correlation_matrix_df.columns:
                raise ValueError(f"Technology '{technology}' not found in technology correlation matrix")
        for country in project_countries.values():
            if country not in country_correlation_matrix_df.index or country not in country_correlation_matrix_df.columns:
                raise ValueError(f"Country '{country}' not found in country correlation matrix")

        # Check for NaN values in the correlation matrices
        if technology_correlation_matrix_df.isnull().any().any() or country_correlation_matrix_df.isnull().any().any():
            raise ValueError("Correlation matrices cannot contain NaN values")

        # Create dictionaries to map project names to their corresponding technologies and countries
        project_technologies = yearly_portfolio_df.set_index('project_name')['technology'].to_dict()
        project_countries = yearly_portfolio_df.set_index('project_name')['country'].to_dict()

        # Get the unique project names
        project_names = yearly_portfolio_df['project_name'].unique()

        # Create an empty correlation matrix with the project names as the row and column indexes
        correlation_matrix = pd.DataFrame(index=project_names, columns=project_names)

        # Iterate over each pair of projects
        for project1 in project_names:
            for project2 in project_names:
                # Get the technologies and countries for the two projects
                tech1 = project_technologies[project1]
                tech2 = project_technologies[project2]
                country1 = project_countries[project1]
                country2 = project_countries[project2]

                # Get the correlations between the two technologies and countries
                tech_correlation = technology_correlation_matrix_df.loc[tech1, tech2]
                country_correlation = country_correlation_matrix_df.loc[country1, country2]

                # Calculate the project correlation as the product of the technology and country correlations
                correlation = tech_correlation * country_correlation

                # Set the correlation in the project correlation matrix
                correlation_matrix.loc[project1, project2] = correlation

        # Convert the correlation matrix to a numpy array
        correlation_matrix_array = correlation_matrix.values

        # Make the correlation matrix symmetric
        correlation_matrix_array = (correlation_matrix_array + correlation_matrix_array.T) / 2

        # Explicitly convert the correlation matrix to a float64 array
        correlation_matrix_array = correlation_matrix_array.astype(np.float64)

        # Make the correlation matrix positive semi-definite
        eigenvalues, eigenvectors = np.linalg.eig(correlation_matrix_array)
        eigenvalues[eigenvalues < 0] = 0
        correlation_matrix_array = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

        # Set the diagonal values to 1
        np.fill_diagonal(correlation_matrix_array, 1)

        return correlation_matrix_array
    except Exception as e:
        print(f"An error occurred while building the project correlation matrix: {e}")
        return np.array([])

def run_portfolio_simulation(yearly_portfolio_df: pd.DataFrame, project_correlation_matrix: list, num_simulations: int = 10000) -> list:
    """
    This function runs a Monte Carlo simulation to estimate the overall portfolio delivery and delivery rate for all years in the portfolio.

    Parameters:
    yearly_portfolio_df (pd.DataFrame): A pandas DataFrame containing the yearly portfolio data.
    project_correlation_matrix (list): A list representing the correlation matrix for the projects.
    num_simulations (int): The number of simulations to run. Defaults to 10000.

    Returns:
    list: A list of tuples, each containing the year, overall standard deviation, overall portfolio delivery, and overall delivery rate.
    """

    results = []
    project_end_years = yearly_portfolio_df['start_year'] + yearly_portfolio_df['contract_duration'] - 1
    last_year = project_end_years.max()
    years = range(yearly_portfolio_df['start_year'].min(), last_year + 1)

    for year in years:
        # Filter the dataframe to include only projects that are active in the current year
        active_projects_df = yearly_portfolio_df[(yearly_portfolio_df['start_year'] <= year) & (yearly_portfolio_df['start_year'] + yearly_portfolio_df['contract_duration'] > year)]

        if not active_projects_df.empty:
            # Get the delivery volumes, standard deviations and offered volumes for the current year
            delivery_volume_means = active_projects_df[f'delivery_volume_{year}'].fillna(0).values
            standard_deviations = active_projects_df[f'standard_deviation_{year}'].fillna(0).values
            offered_volumes = active_projects_df[f'offered_volume_{year}'].fillna(0).values

            # Filter the project correlation matrix to only include active projects
            active_project_indices = yearly_portfolio_df.index.isin(active_projects_df.index)
            active_project_correlation_matrix = np.array(project_correlation_matrix)[active_project_indices, :][:, active_project_indices]

            # Calculate the Cholesky decomposition of the correlation matrix
            cholesky_factors = np.linalg.cholesky(active_project_correlation_matrix)

            # Generate random samples from a multivariate normal distribution
            samples = delivery_volume_means + np.dot(np.random.normal(size=(num_simulations, len(delivery_volume_means))), np.dot(np.diag(standard_deviations), cholesky_factors))

            # Calculate the total portfolio outcome by summing the samples across all projects
            overall_portfolio = np.sum(samples, axis=1)

            # Calculate the standard deviation of the total portfolio outcomes
            std_dev_overall_portfolio = np.std(overall_portfolio)

            # Calculate the overall offered volume
            overall_offered_volume = np.sum(offered_volumes)

            # Calculate the overall portfolio delivery
            # We subtract 2 times the standard deviation from the overall offered volume to get the overall portfolio delivery
            overall_portfolio_delivery = overall_offered_volume - (2 * std_dev_overall_portfolio)

            # Calculate the overall delivery rate
            # We divide the overall portfolio delivery by the overall offered volume to get the overall delivery rate
            overall_delivery_rate = overall_portfolio_delivery / overall_offered_volume

            results.append((year, std_dev_overall_portfolio, overall_portfolio_delivery, overall_delivery_rate, overall_offered_volume))
            
    return results