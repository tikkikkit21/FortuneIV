import sys
from pathlib import Path
import pandas as pd
from typing import Tuple
from helpers import load_json

DATE_COLUMN_HEADER = 'Date'
CELL_B16 = (15,1)
LOCATION_NOT_FOUND = (-1,-1)

def format_report_file(csv_file: str) -> None:
    """Formats a CSV file so 'Date' column header is at A1 and any extra data
    above or to the left is deleted.

    Args:
        csv_file (string): Path to CSV file to format
    """
    # validate path and read CSV file
    if not Path(csv_file).is_file():
        print(f'Error: File {csv_file} does not exist.')
        sys.exit(1)
    df = pd.read_csv(csv_file, header=None)

    # find location of 'Date' column header
    date_row, date_col = find_date_cell(df)
    if ((date_row, date_col) == LOCATION_NOT_FOUND):
        print(f'Error: \'{DATE_COLUMN_HEADER}\' header not found in CSV.')
        return

    # format report file
    df = move_data_to_a1(df, date_row, date_col)
    df = trim_rows(df)
    df = trim_whitespace(df)
    df = replace_values(df)

    # export
    df.to_csv(csv_file, index=False)
    print(f'{csv_file} reformatted successfully.')

def find_date_cell(df: pd.DataFrame) -> Tuple[int,int]:
    """Searches for the location of the 'Date' column header.

    Args:
        df (DataFrame): Pandas DataFrame representation of the CSV file

    Returns:
        Tuple[int,int]: Row and column index of the Date cell (0-based)
    """
    date_row, date_col = (0,0)

    # check B16 first for 'Date' column
    b16_exists = df.shape[0] > CELL_B16[0] and df.shape[1] > CELL_B16[1]
    if b16_exists and str(df.iat[CELL_B16]).strip() == DATE_COLUMN_HEADER:
        date_row, date_col = CELL_B16

    # search entire spreadsheet
    else:
        found = False
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                if str(df.iat[r, c]).strip() == DATE_COLUMN_HEADER:
                    date_row, date_col = r, c
                    found = True
                    break
            if found:
                break
        if not found:
            date_row, date_col = LOCATION_NOT_FOUND

    return date_row, date_col

def move_data_to_a1(df: pd.DataFrame, date_row: int, date_col: int) -> pd.DataFrame:
    """Moves the 'Date' column header to be A1

    Args:
        df (pd.DataFrame): DataFrame representing CSV file to format
        date_row (int): 0-based row index of 'Date'
        date_col (int): 0-based column incdes of 'Date'

    Returns:
        pd.DataFrame: Formatted DataFrame with 'Date' at A1
    """
    new_headers = df.iloc[date_row, date_col:]
    new_data = df.iloc[date_row + 1:, date_col:]
    new_data.columns = new_headers
    new_data.reset_index(drop=True, inplace=True)
    return new_data

def trim_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Removes empty and net/total rows

    Args:
        df (pd.DataFrame): DataFrame representing CSV file to format

    Returns:
        pd.DataFrame: Formatted DataFrame with unecessary rows removed
    """
    # remove empty rows
    new_data = df.dropna(how='all')

    # remove last row if it's a Net or Total amount
    last_value = str(new_data.iloc[-1, 1]).strip().lower() if len(new_data.columns) > 1 else ''
    if last_value in ['net', 'total']:
        new_data = new_data.iloc[:-1]

    return new_data

def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Trims whitespace around each cell value

    Args:
        df (pd.DataFrame): DataFrame representing CSV file to format

    Returns:
        pd.DataFrame: Formatted DataFrame with extra whitespace trimmed
    """
    return df.replace(r'^\s+|\s+$', '', regex=True)

def replace_values(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces cell values with new value according to replacement info

    Args:
        df (pd.DataFrame): DataFrame representing CSV file to format

    Returns:
        pd.DataFrame: Formatted DataFrame with specified values updated
    """
    replacement_info = load_json('config/replacement_map.json')
    print(replacement_info)
    return df.replace(replacement_info)

if __name__ == '__main__':
    # fetch filename from CLI
    if len(sys.argv) < 2:
        print('Usage: python format_report.py <csv_file|directory>')
        sys.exit(1)
    path_arg = Path(sys.argv[1])

    # format report file
    if path_arg.is_file() and path_arg.suffix.endswith('.csv'):
        format_report_file(str(path_arg))
    elif path_arg.is_dir():
        for file_path in path_arg.rglob('*.csv'):
            format_report_file(str(file_path))
