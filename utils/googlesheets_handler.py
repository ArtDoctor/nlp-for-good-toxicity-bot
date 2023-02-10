import gspread

account = gspread.service_account(filename='utils/key.json')

sheet = account.open('Toxicity Data Labeling')
work_sheet = sheet.worksheet('Sheet1')

insertRow = ["hello", 5, "red", "blue"]


def append_new_cell(is_toxic, message):
    if is_toxic:
        col = 1
    else:
        col = 2
    row = len(work_sheet.col_values(col)) + 1
    work_sheet.update_cell(row, col, message)


