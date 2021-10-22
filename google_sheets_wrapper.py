import gspread
import os
import time
import pathlib

class google_sheet():
    def __init__(self, service_account_file="", sheet_name="", sheet_id=""):
        """
        Initialize Google Sheet class.
        Note: Sheet is Google spreadsheet, while worksheet is a sheet/subsheet/tab. Google vs Gspread naming is slightly different, gspread was chosen.
        :param service_account_file: string: Service account file. If blank, will look for "google_sheets_key.json" in current directory.
        :param sheet_name: string: Name of Google Sheet to use. If not used, ID will be used.
        :param sheet_id: string: ID of Google Sheet to use. If not used, Name will be used. If both are supplied, ID will be used.
        """
        if not service_account_file:
            service_account_file = pathlib.Path(os.path.dirname(os.path.abspath(__file__)) + "/" + "google_sheets_key.json")

        self.gc = gspread.service_account(service_account_file)

        if not sheet_name and not sheet_id:
            print("Provide either a sheet name or sheet id")

        self.sheet_name = sheet_name
        self.sheet_id = sheet_id

        # Both sheet_name and sheet_id should be populated at end of initialization.
        if sheet_name:
            self.sheet_id = self.open_sheet()['sheet_id']

        if sheet_id:
            self.sheet_name = self.open_sheet()['sheet_name']

    def create_sheet(self, name=""):
        """
        Create a Google spreadsheet from name provided.
        :return: string: Google Sheet ID.
        """
        if not name and not self.sheet_name:
            return self.gc.create("Change_me_random_{}".format(str(int(time.time())))).id
        elif name:
            return self.gc.create(name).id
        else:
            return self.gc.create(self.sheet_name).id

    def delete_sheet(self, file_id):
        """
        Delete a Google spreadsheet based on ID provided.
        :param file_id: string: Google Sheet ID.
        :return: boolean: True if deleted successfully, False if not.
        """
        try:
            self.gc.del_spreadsheet(file_id=file_id)
            return True
        except:
            return False

    def open_sheet(self):
        """
        Get the either spreadsheet title or ID from the item provided. Examle: Name should return ID and vice versa.
        :return: dict: {'sheet_name': 'value', 'sheet_id': 'value'}
        """
        if self.sheet_id:
            return {'sheet_name': self.gc.open_by_key(self.sheet_id).title, 'sheet_id': self.sheet_id}
        else:
            return {'sheet_name': self.sheet_name, 'sheet_id': self.gc.open(self.sheet_name).id}

    def share_sheet(self, user, perm_type='user', role='writer'):
        """
        Share Google Sheet with a email address.
        :param user: string: Email address of person to share Google spreadsheet with.
        :param perm_type: string: Permission type, only tested with user. Need to look into more if used more.
        :param role: string: Role of user for spreadsheet. Again, need to look into more if used more. I think, this is editor, commenter, viewer.
        :return: boolean: True if shared successfully, False if not.
        """
        try:
            # Should migrate to sheet_id, once this is working.
            self.gc.open(self.sheet_name).share(user, perm_type=perm_type, role=role)
            return True
        except:
            return False

    def create_worksheet(self, worksheet_name, rows="0", cols="0"):
        """
        Create a worksheet in a within a spreadsheet.
        :param worksheet_name: string: Name of the worksheet to be created.
        :param rows: string: Number of rows to create. 0 is default unlimited.
        :param cols: string: Number of columns to create. 0 is default unlimited.
        :return: int: ID of the worksheet.
        """
        return self.gc.open(self.sheet_name).add_worksheet(title=worksheet_name, rows=rows, cols=cols).id

    def delete_worksheet(self, worksheet_name):
        """
        Delete a worksheet in a within a spreadsheet.
        :param worksheet_name: string: Name of the worksheet to be created.
        :return: boolean: True if deleted successfully, False if not.
        """
        try:
            self.gc.open(self.sheet_name).del_worksheet(worksheet=sh.worksheet(worksheet_name))
            return True
        except:
            return False

    def get_all_worksheets(self):
        """
        Get names of all worksheets in a spreadsheet.
        :return: list: List of all worksheet names.
        """
        sh = self.gc.open(self.sheet_name)
        return [ws for ws in sh.worksheets()]

    def check_worksheet_exist(self, worksheet_name):
        """
        Check if worksheet name provided is found within all worksheets currently in spreadsheet. Case insensitive.
        :param worksheet_name: string: Name of the worksheet to look for.
        :return: int/boolean: ID of worksheet if found, if not found empty string. Note: 0 is common, so don't do "if not".
        """
        worksheet = [ws for ws in self.gc.open(self.sheet_name).worksheets() if ws.title.lower() == worksheet_name.lower()]
        if worksheet:
            return worksheet[0].id
        return False

    def upload_list(self, worksheet_name, list_to_upload, append=True):
        """
        Upload a nested list of lists (or dicts) to a worksheet.
        :param worksheet_name: string: Name of worksheet to upload to.
        :param list_to_upload: list: Nest list of list (or dicts) to upload. First part of this method converts nested dicts to nested lists.
        :param append: boolean: If True append lists to bottom of worksheet, if False write over.
        :return: boolean: True if completed successfully, False if not.
        """
        if type(list_to_upload[0]) is dict:
            tmp_list = [[k for k in list_to_upload[0].keys()]]
            for _d in list_to_upload:
                tmp_list.append([v for v in _d.values()])
            list_to_upload = list(tmp_list)

        sh = self.gc.open(self.sheet_name)
        try:
            if append:
                sh.values_append(
                    '{}!A1'.format(worksheet_name),
                    params={'valueInputOption': 'RAW'},
                    body={'values': list_to_upload}
                )
            else:
                sh.values_update(
                    '{}!A1'.format(worksheet_name),
                    params={'valueInputOption': 'RAW'},
                    body={'values': list_to_upload}
                )
            return True
        except:
            return False

    def get_row_value(self, worksheet_name: str, row: str):
        """
        Get row of values from worksheet and return as a nested list.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :param row: string: Row number to pull data from. Starts at 1.
        :return: list: List of values.
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).row_values(row)

    def get_column_value(self, worksheet_name: str, column: str):
        """
        Get column of values from worksheet and return as a nested list.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :param column: string: Column number, not letter, to pull data from. Starts at 1.
        :return: list: List of values.
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).col_values(column)

    def get_cell_value(self, worksheet_name: str, cell: str):
        """
        Get cell of values from worksheet and return as a string.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :param cell: string: Cell value to pull data from. Example: A2 is column A row value 2.
        :return: string: Value of cell.
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).acell(cell).value

    def get_all_values_list(self, worksheet_name):
        """
        Return all rows of worksheet as a nested list.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :return: list: Nested list of lists with all values. Header row is main list index 0.
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).get_all_values()

    def get_all_values_dict(self, worksheet_name):
        """
        Return all rows of worksheet as a nested dictionary.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :return: list: Nested list of dictionaries. Header row is turned into key and all subsequent rows are values. Expected to have n-1 number of rows from sheet.
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).get_all_records()

    def clear_worksheet(self, worksheet_name):
        """
        Clear all values from a worksheet.
        :param worksheet_name: string: Name of worksheet you wish to pull information from.
        :return: dict: Sheet ID value and range cleared. Example: {'spreadsheetId': 'sheet_id_value', 'clearedRange': 'Sheet1!A1:Z1000'}
        """
        return self.gc.open(self.sheet_name).worksheet(worksheet_name).clear()

def main():
    pass

if __name__ == '__main__':
    main()