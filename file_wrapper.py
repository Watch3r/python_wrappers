import json
import os
import csv
import zipfile
import codecs
import logging


class file_io():
    def __init__(self, file_name):
        """
        Initialize class with a filename you will be working on. Full file path is optional.
        :param file_name: string: name of file
        """
        self.file_name = file_name

    def read_file(self, return_list=False, cleaned=True):
        """
        Read a file using utf-8 and ignore errors.
        :param return_list: boolean: True returns each line as nested list.
        :param cleaned: boolean: True runs .strip on each item before putting it into a list.
        :return: Either a nested list or a string of full file contents. Depends on parameters set.
        """
        with open(self.file_name, 'r', newline='', encoding='utf-8', errors='ignore') as file:
            if return_list and cleaned:
                return [line.strip() for line in file.read().split("\n")]
            elif return_list and not cleaned:
                return file.readlines()
            return file.read()

    def write_file_new(self, text_to_write, add_newline=True):
        """
        Write content to a file. If the file already exists, it will be overwritten.
        :param text_to_write: string: Content to write in the file.
        :param add_newline: boolean: True adds a new line to the end of the content.
        :return:
        """
        with open(self.file_name, 'w+', newline='', encoding='utf-8', errors='ignore') as file:
            if add_newline:
                file.write(text_to_write + "\n")
            else:
                file.write(text_to_write)

    def write_file_append(self, text_to_write, add_newline=True):
        """
        Open a file and append text to the end of it. The original content is kept.
        :param text_to_write: string: Content to write in the file.
        :param add_newline: boolean: True adds a new line to the end of the content.
        :return:
        """
        with open(self.file_name, 'a+', newline='', encoding='utf-8', errors='ignore') as file:
            if add_newline:
                file.write(text_to_write + "\n")
            else:
                file.write(text_to_write)

    def write_csv_from_dict(self, fieldnames: list, dict_to_write: list):
        """

        :param fieldnames: List of fieldnames
        :param dict_to_write: List of nested dicts
        :return:
        """
        with open(self.file_name, 'w+', newline='', encoding='utf-8', errors='ignore') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in dict_to_write:
                writer.writerow(i)

    def read_csv(self):
        """
        Read CSV file to nested list.
        :return: list: nested list of CSV file.
        """
        with open(self.file_name, newline='\n', encoding='utf-8', errors='ignore') as f:
            return [row for row in csv.reader(f)]

    def write_csv(self, list_to_write):
        """
        Write a nested list of lists to a csv file.
        :param list_to_write: list: nested list to write.
        :return: boolean: True if successfully finished, False if not.
        """
        try:
            with open(self.file_name, mode='w+', newline="\n") as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                for row in list_to_write:
                    writer.writerow(row)
            return True
        except:
            return False

    def read_json(self):
        with open(self.file_name, 'r', newline='\n', encoding='utf-8', errors='ignore') as json_file:
            return json.load(json_file)

    def write_json(self, json_data):
        with open(self.file_name, 'w+') as outfile:
            json.dump(json_data, outfile)

    def read_file_hex_dump(self):
        """
        Returns a hex dump of file contents.
        :return: bytes: Hex dump of file contents.
        """
        tmp = []
        with open(self.file_name, 'rb') as file:
            for chunk in iter(lambda: file.read(32), b''):
                tmp.append(codecs.encode(chunk, 'hex'))
        return tmp


class file_work():
    def check_file_exists(self, file_name: str, add_cwd=False):
        """
        Check if file exists on local file system.
        :param file_name: str of filename
        :param add_cwd: boolean
        :return: string: Path of file.
        """
        if add_cwd:
            return os.path.isfile(os.path.join(os.getcwd(), file_name))

        return os.path.isfile(file_name)

    def delete_files(self, path="", starts_with="", ends_with="", file_is=""):
        """
        Delete all files in directory that meet your naming requirements.
        :param path: string: Path you wish to work from, if empty it will be cwd of the script.
        :param starts_with: string: If the filename starts with this combination it will be deleted.
        :param ends_with: string: If the filename ends with this combination it will be deleted.
        :param file_is: string: If the filename matches with file_is it will be deleted.
        :return: list: List of deleted files.
        """
        deleted_files = []
        if not path:
            path = os.getcwd()

        for i in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            if starts_with or ends_with:
                if i.startswith(starts_with) and i.endswith(ends_with):
                    deleted_files.append(i)
                    os.remove(i)
            if file_is:
                if i == file_is:
                    deleted_files.append(i)
                    os.remove(i)

        return list(set(deleted_files))

    def bulk_file_select(self, path="", starts_with="", ends_with="", file_is=""):
        """
        List all files in directory that meet your naming requirements.
        :param path: string: Path you wish to work from, if empty it will be cwd of the script.
        :param starts_with: string: If the filename starts with this combination it will be returned.
        :param ends_with: string: If the filename ends with this combination it will be returned.
        :param file_is: string: If the filename matches with file_is it will be returned.
        :return: list: List of found files that meet naming requirements.
        """
        return_list = []
        if not path:
            path = os.getcwd()

        for i in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            if starts_with or ends_with:
                if i.startswith(starts_with) and i.endswith(ends_with):
                    return_list.append(i)
            if file_is:
                if i == file_is:
                    return_list.append(i)
        return return_list

    def list_selection(self, message: str, opts: list):
        """
        Provide a message and list of options with corresponding numbers so a user can select an item.
        :param message: string: Message to provide context around options.
        :param opts: list: List of items to list as options.
        :return: string: Selected value from list based on selection.
        """
        while True:
            print(message)
            print("Make your selection:")
            for num, opt in enumerate(opts, start=1):
                print("{}: {}".format(str(num), str(opt)))
            choice = input("Enter corresponding number to option: ")
            try:
                choice = int(choice)
            except:
                print("Enter a number.")
                continue
            if choice < 1 or choice > len(opts):
                print("Make a choice from 1 - {}".format(str(len(opts))))
                continue
            return opts[choice - 1]


class file_process():
    def __init__(self, file_name):
        """
        Initialize class with a filename you will be working on. Full file path is optional.
        :param file_name: string: name of file
        """
        self.file_name = file_name

    def unzip(self, extract_dir=""):
        """
        Unzip a zip file to a directory or cwd.
        :param extract_dir: string: Directory to unzip files to.
        :return: boolean: True if unzipped successfully, False if not.
        """
        if not extract_dir:
            extract_dir = os.getcwd()

        try:
            with zipfile.ZipFile(self.file_name, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except:
            return False


class logger():
    def log(self, message, file_name, sev=5, debug=False):
        """
        Log a message to a file using Python logging.
        :param message: string: Message to log to a file.
        :param file_name: string: Filename where to log message.
        :param sev: int: Severity (1-5) of message to log. 1:Critical, 2:Error, 3:Warning, 4:Info, 5:Debug (5:catch all)
        :param debug: boolean: To enable debug logging, this captures more but is very noisy and not always wanted.
        :return: boolean: True if successfully logged, False if not.
        """
        try:
            log_level = logging.INFO if not debug else logging.DEBUG
            logging.basicConfig(filename=file_name, level=log_level, format="%(asctime)s:%(levelname)s:%(message)s", datefmt='%Y-%m-%d %H:%M:%S')
            logging.critical(message) if sev == 1 else logging.error(message) if sev == 2 else logging.warning(message) if sev == 3 else logging.info(message) if sev == 4 else logging.debug(message)
            return True
        except:
            return False


if __name__ == '__main__':
    pass
