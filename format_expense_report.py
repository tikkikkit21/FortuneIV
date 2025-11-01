import sys
from pathlib import Path
import pandas as pd

# fetch filename from CLI
if len(sys.argv) < 2:
    print('Usage: python format_expense_report.py <filename.csv>')
    sys.exit(1)

csv_file = Path(sys.argv[1])
if not csv_file.is_file():
    print(f'Error: File {csv_file} does not exist.')
    sys.exit(1)

# Load CSV without headers
df = pd.read_csv(csv_file, header=None, dtype=str)

# check B16 first for 'Date' column
DATE_COLUMN_HEADER = 'Date'
B16 = 15, 1
b16_exists = df.shape[0] > B16[0] and df.shape[1] > B16[1]
if b16_exists and str(df.iat[B16]).strip() == DATE_COLUMN_HEADER:
    row_start, col_start = B16

# search entire spreadsheet
else:
    row_start = col_start = 0
    found = False
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            if str(df.iat[r, c]).strip() == DATE_COLUMN_HEADER:
                row_start, col_start = r, c
                found = True
                break
        if found:
            break
    if not found:
        print(f'Error: \'{DATE_COLUMN_HEADER}\' header not found in CSV.')
        sys.exit(1)

# move Date column to be A1 (upper leftmost cell)
new_headers = df.iloc[row_start, col_start:]
new_data = df.iloc[row_start + 1:, col_start:]
new_data.columns = new_headers
new_data.reset_index(drop=True, inplace=True)

# export
new_data.to_csv(csv_file, index=False)
print(f'{csv_file} reformatted successfully.')
