## GHG_Port

### Introduction

The GHG_Port project is a Python-based tool designed to analyze the risk of a portfolio of Greenhouse Gas (GHG) reduction projects. It utilizes Monte Carlo simulations to assess the potential risks and outcomes of a given portfolio, providing valuable insights for informed decision-making. The project takes as input an Excel file containing portfolio data and generates output files with the results of the simulation. This tool is intended for use by organizations and individuals involved in GHG reduction projects who seek to better understand and manage the risks associated with their investments.

### Requirements

The GHG_Port project requires the following Python libraries to be installed:

See requirements.txt for a full list of required libraries.
You can install the required libraries using pip:

`pip install -r requirements.txt`

Usage

To run the GHG_Port project, navigate to the directory containing the `GHG_Port.py` file and run the following command:

`python GHG_Port.py`
By default, the program will look for an input file named `GHG_Portfolio_Data.xlsx` in the data directory. If you want to specify a different input file, you can use the -i option followed by the name of the file:

`python GHG_Port.py -i your_input_file.xlsx`
Note that the input file must be located in the `data` directory. The program will generate output files in a timestamped directory within the `output` directory.

### Input File Format
The input file for the GHG_Port project is an Excel file with the following worksheets:

- Portfolio
- Technology Correlation Matrix
- Country Correlation Matrix

#### Portfolio

The Portfolio worksheet should contain the following columns for each project in the portfolio:

| Column Name | Description |
|-------------|-------------|
| project_id  | Unique identifier for the project |
| project_name | Name of the project |
| contract_duration | Duration of the project contract |
| country | Country where the project is located |
| technology | Technology used in the project |
| counterparty | Counterparty involved in the project |
| start_year | Start year of the project |
| screening_date | Screening date for the project |
| offered_volume_year_1-10 | Offered volume for each year of the project (up to 10 years) |
| project_standard_deviation_year_1-10 | Standard deviation of the project for each year (up to 10 years) |
| project_delivery_volume_year_1-10 | Delivery volume of the project for each year (up to 10 years) |
| project_expected_value_percentage_year_1-10 | Expected value percentage of the project for each year (up to 10 years) |
| overall_project_rating | Overall rating of the project |

#### Technology and Country Correlation Matrices

The Technology Correlation Matrix and Country Correlation Matrix worksheets should contain the correlation coefficients between each pair of technologies/countries in the portfolio. The correlation coefficients should be between -1 and 1.

Here is an example of what the Technology Correlation Matrix might look like:

| Technology | Waste-to-Energy | Carbon Capture | Energy Efficiency | ... |
|------------|-----------------|----------------|------------------| ... |
| Waste-to-Energy | 1 | 0.295162943 | -0.126402483 | ... |
| Carbon Capture | 0.295162943 | 1 | 0.079969733 | ... |
| Energy Efficiency | -0.126402483 | 0.079969733 | 1 | ... |
| ... | ... | ... | ... | ... |
Note that the correlation coefficients should be symmetric, i.e. the correlation between Technology A and Technology B is the same as the correlation between Technology B and Technology A.

Similarly, the Country Correlation Matrix should contain the correlation coefficients between each pair of countries in the portfolio.

#### Default Rates and Recovery Potential

The Default Rates and Recovery Potential worksheets should contain the default rates and recovery potential for each investment grade and year.

The Default Rates table should have the following structure:

| Investment Grade | Year 1 | Year 2 | Year 3 | ... | Year 10 |
|------------------|--------|--------|--------| ... |--------|
| Investment       | 0.14   | 0.37   | 0.64   | ... | 3.08   |
| Speculative      | 4.49   | 8.91   | 12.81  | ... | 26.46  |
| C                | 27.58  | 38.13  | 44.28  | ... | 56.51  |

The Recovery Potential table should have a similar structure, with the same investment grades and years.

### Simulation Process

1. `create_yearly_portfolio` is responsible for transforming the input portfolio DataFrame into a yearly portfolio DataFrame. This involves several steps:
- Data validation: The function checks if the input DataFrame is empty and if it contains all the required columns.
- Data transformation: The function melts the offered_volume_year_i columns into a single column, extracts the year index from the variable names, and calculates the corresponding calendar year.
- Data cleaning: The function drops rows with missing values and extracts the variable name from the variable column.
- Data pivoting: The function pivots the DataFrame to get the desired output format, with separate columns for each variable (offered volume, standard deviation, delivery volume, expected value percentage) and each calendar year.
- Data reordering: The function reorders the columns so that similar columns are together, making it easier to analyze and process the data.

2. `build_project_correlation_matrix` is responsible for constructing a correlation matrix between projects in the portfolio.
- Data validation: The function checks if the input DataFrames are empty, if they contain all the required columns, and if the project names, technologies, and countries in the yearly portfolio DataFrame exist in the correlation matrices.
- Data preparation: The function creates dictionaries to map project names to their corresponding technologies and countries, and gets the unique project names.
- Correlation calculation: The function calculates the correlation between each pair of projects as the product of the correlations between their technologies and countries.
- Matrix construction: The function constructs a correlation matrix with the project names as the row and column indexes, and sets the calculated correlations in the matrix.
- Matrix processing: The function makes the correlation matrix symmetric, explicitly converts it to a float64 array, and ensures it is positive semi-definite by adjusting the eigenvalues.
- Finalization: The function sets the diagonal values of the correlation matrix to 1 and returns the resulting matrix as a numpy array.

3. `run_portfolio_simulation` is responsible for running a Monte Carlo simulation to estimate the overall portfolio delivery and delivery rate for all years in the portfolio.
- Data preparation: The function filters the yearly portfolio DataFrame to include only projects that are active in the current year, and extracts the delivery volumes, standard deviations, and offered volumes for the current year.
- Correlation matrix processing: The function filters the project correlation matrix to only include active projects, and calculates the Cholesky decomposition of the correlation matrix.
- Simulation: The function generates random samples from a multivariate normal distribution using the Cholesky decomposition, and calculates the total portfolio outcome by summing the samples across all projects.
- Risk analysis: The function calculates the standard deviation of the total portfolio outcomes, and uses it to estimate the overall portfolio delivery and delivery rate.
- Results aggregation: The function returns a list of tuples, each containing the year, overall standard deviation, overall portfolio delivery, overall delivery rate, and overall offered volume.

### Known Issues

The project correlation matrix is constructed from manually assigned technology and country correlations, which can lead to issues with positive semi-definiteness. If the correlation matrix is not positive semi-definite, the simulation will fail. This is a known limitation of the current implementation, and users should be aware of this potential issue when using the tool.

### Output
The project produces one Excel file as output: Portfolio_Simulation_Results.xlsx. This file is stored in a timestamped directory within the /output subdirectory. The directory is created at runtime and its name is in the format YYYYMMDD_HHMMSS, where YYYYMMDD is the date and HHMMSS is the time.

Portfolio Simulation Results
The Portfolio_Simulation_Results.xlsx file contains the results of the portfolio simulation. It has two worksheets:

- Simulation Results: This worksheet contains the results of the simulation, including the year, offered volume, portfolio delivery, standard deviation, and delivery rate.
- Yearly Portfolio: This worksheet contains the projects that were used in the simulation, including the year and project name.

### Generating a Random Portfolio

The `generate_portfolio.py` script, located in the scripts directory, can be used to generate a random portfolio of projects and corresponding correlation matrices. This can be useful for testing and demonstration purposes.

To use the script, run it from the command line with the following options:

- -i: Input file name (default: GHG_Test_Projects.xlsx)
- -s: Portfolio size (default: 10)
- -csv: Export portfolio to CSV file (default: False)

For example:

`python generate_portfolio.py -i GHG_Test_Projects.xlsx -s 20 -csv`
This will generate a random portfolio of 20 projects and export it to a CSV file named `GHG_Portfolio.csv` in the data directory.

Note that the script uses the `GHG_Test_Projects.xlsx` file as input by default, but you can specify a different input file using the -i option. The script also generates random correlation matrices for the technologies and countries in the portfolio.

### License and Credits

This GHG_Port project is released under the Creative Commons Attribution 4.0 International License.

### Conclusion

The GHG_Port project provides a powerful tool for analyzing the risks associated with a portfolio of greenhouse gas reduction projects. By using Monte Carlo simulations to estimate the overall portfolio delivery and delivery rate, the project enables users to make more informed decisions about their investments. While the project has some known limitations, such as the potential for issues with positive semi-definiteness in the project correlation matrix, it provides a valuable resource for anyone looking to better understand the risks and opportunities associated with GHG reduction projects.