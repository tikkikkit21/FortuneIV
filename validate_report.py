import sys
from pathlib import Path
import pandas as pd
from typing import List
from helpers import load_json_root

PRINT_DIVIDER = '-'*50

# load info from JSON files
ALLOWED_CATEGORIES = load_json_root('config/categories.json')
ALLOWED_METHODS    = load_json_root('config/payment_methods.json')
REQUIRED_COLUMNS   = load_json_root('config/required_values.json')

def validate_report_file(csv_file: str) -> bool:
    """Validates a single expense report CSV file.

    Args:
        csv_file (string): path to CSV file to validate

    Returns:
        bool: true if all criteria pass, false otherwise
    """
    print(PRINT_DIVIDER)
    print(f'Validating {csv_file}...')
    is_valid = True
    # validate path and read CSV file
    if not Path(csv_file).is_file():
        print(f'Error: File {csv_file} does not exist.')
        return False
    df = pd.read_csv(csv_file)

    # check for missing required fields
    missing_mask = df[REQUIRED_COLUMNS].isna() | (df[REQUIRED_COLUMNS] == '')
    if missing_mask.any().any():
        print('Missing values found in critical columns:')
        print_invalid_data(df[REQUIRED_COLUMNS][missing_mask.any(axis=1)])
        is_valid = False

    # validate categories and payment methods
    invalid_categories = df[~df['Category'].isin(ALLOWED_CATEGORIES)]
    if not invalid_categories.empty:
        print('Invalid category values found:')
        print_invalid_data(invalid_categories[['Category']])
        is_valid = False

    invalid_methods = df[~df['w/'].isin(ALLOWED_METHODS)]
    if not invalid_methods.empty:
        print('Invalid payment method values found:')
        print_invalid_data(invalid_methods[['w/']])
        is_valid = False

    # check that all non-missing dates belong to the same month and year
    if 'Date' in df.columns:
        dates = pd.to_datetime(df['Date'], errors='coerce')
        valid_dates = dates.dropna()
        if len(valid_dates) > 0:
            # extract year-month periods
            periods = valid_dates.dt.to_period('M')
            # find the most common month-year
            common_period = periods.mode()[0]
            # find the odd-one-out dates
            odd_ones = valid_dates[periods != common_period]
            if len(odd_ones) > 0:
                print('Dates not in the common month/year:')
                print(odd_ones)
                is_valid = False

    return is_valid

def print_invalid_data(invalid_data: pd.DataFrame) -> None:
    """Helper function to print out invalid data

    Args:
        data (pd.DataFrame): invalid data to print out
    """
    print(invalid_data.to_string(index=False))

if __name__ == '__main__':
    # fetch filename from CLI
    if len(sys.argv) < 2:
        print('Usage: python validate_report.py <csv_file|directory>')
        sys.exit(1)
    path_arg = Path(sys.argv[1])

    # validate report file
    is_valid = True
    if path_arg.is_file() and path_arg.suffix.endswith('.csv'):
        is_valid &= validate_report_file(str(path_arg))
    elif path_arg.is_dir():
        for file_path in path_arg.rglob('*.csv'):
            is_valid &= validate_report_file(str(file_path))

    # print result
    if is_valid:
        print('All report files were validated succesfully.')
    else:
        print('One or more report files have issues.')
