import sys
from pathlib import Path
import pandas as pd
from typing import Tuple

DATE_COLUMN_HEADER = 'Date'

def find_date_cell(df: pd.DataFrame) -> Tuple[int,int]:
    """Searches for the location of the 'Date' column header.

    Args:
        df (DataFrame): Pandas DataFrame representation of the CSV file

    Returns:
        Tuple[int,int]: row and column index of the Date cell (0-based)
    """
    date_row, date_col = (0,0)

    # check B16 first for 'Date' column
    B16 = (15,1)
    b16_exists = df.shape[0] > B16[0] and df.shape[1] > B16[1]
    if b16_exists and str(df.iat[B16]).strip() == DATE_COLUMN_HEADER:
        date_row, date_col = B16

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
            print(f'Error: \'{DATE_COLUMN_HEADER}\' header not found in CSV.')
            sys.exit(1)
    
    return date_row, date_col

def format_report_file(csv_file: str) -> None:
    """Formats a CSV file so 'Date' column header is at A1 and any extra data
    above or to the left is deleted.

    Args:
        csv_file (string): path to CSV file to format
    """

    # validate and read CSV file
    if not Path(csv_file).is_file():
        print(f'Error: File {csv_file} does not exist.')
        sys.exit(1)

    df = pd.read_csv(csv_file, header=None, dtype=str)

    # find location of 'Date' column header
    date_row, date_col = find_date_cell(df)

    # move Date column to be A1 (upper leftmost cell)
    new_headers = df.iloc[date_row, date_col:]
    new_data = df.iloc[date_row + 1:, date_col:]
    new_data.columns = new_headers
    new_data.reset_index(drop=True, inplace=True)

    # export
    new_data.to_csv(csv_file, index=False)
    print(f'{csv_file} reformatted successfully.')

if __name__ == '__main__':
    # fetch filename from CLI
    if len(sys.argv) < 2:
        print('Usage: python format_expense_report.py <csv_file|directory>')
        sys.exit(1)
    path_arg = Path(sys.argv[1])

    # format report file
    if path_arg.is_file() and path_arg.suffix.endswith('.csv'):
        format_report_file(str(path_arg))
    elif path_arg.is_dir():
        for file_path in path_arg.rglob('*.csv'):
            format_report_file(str(file_path))
