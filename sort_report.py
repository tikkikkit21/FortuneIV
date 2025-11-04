import sys
from pathlib import Path
import pandas as pd

DATE_COLUMN_HEADER = 'Date'
DATETIME_FORMAT = '%m/%d/%Y'

def sort_report_file(csv_file: str) -> None:
    """Sorts the entries in a report file based on Date. Assumes that the 'Date'
    column is the first one, use format_expense_report.py to process reports
    before sorting.

    Args:
        csv_file (string): path to CSV file to format
    """

    # validate path and read CSV file
    if not Path(csv_file).is_file():
        print(f'Error: File {csv_file} does not exist.')
        sys.exit(1)
    df = pd.read_csv(csv_file)

    # process CSV
    df[DATE_COLUMN_HEADER] = pd.to_datetime(df[DATE_COLUMN_HEADER], errors='coerce')
    df_sorted = df.sort_values(by=DATE_COLUMN_HEADER)
    df_sorted[DATE_COLUMN_HEADER] = df_sorted[DATE_COLUMN_HEADER].dt.strftime(DATETIME_FORMAT)

    # export
    df_sorted.to_csv(csv_file, index=False)
    print(f'{csv_file} sorted by date successfully.')

if __name__ == '__main__':
    # fetch filename from CLI
    if len(sys.argv) < 2:
        print('Usage: python sort_report.py <csv_file|directory>')
        sys.exit(1)
    path_arg = Path(sys.argv[1])

    # sort report file
    if path_arg.is_file() and path_arg.suffix.endswith('.csv'):
        sort_report_file(str(path_arg))
    elif path_arg.is_dir():
        for file_path in path_arg.rglob('*.csv'):
            sort_report_file(str(file_path))
