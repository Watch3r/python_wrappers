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

    def write_csv_from_dict(self, fieldnames:list, dict_to_write:list):
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
        rows = []
        with open(self.file_name, newline='\n', encoding='utf-8', errors='ignore') as f:
            for row in csv.reader(f):
                rows.append(row)

        return rows

    def write_csv(self, list_to_write):
        with open(self.file_name, mode='w+', newline="\n") as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in list_to_write:
                writer.writerow(row)

    def read_json(self):
        with open(self.file_name, 'r', newline='\n', encoding='utf-8', errors='ignore') as json_file:
            return json.load(json_file)

    def write_json(self, json_data):
        with open(self.file_name, 'w+') as outfile:
            json.dump(json_data, outfile)

    def read_file_hex_dump(self):
        """
        Returns a hex dump of file contents.
        :return: bytes: Hex dump
        """
        tmp = []
        with open(self.file_name, 'rb') as file:
            for chunk in iter(lambda: file.read(32), b''):
                tmp.append(codecs.encode(chunk, 'hex'))
        return tmp

class file_work():
    def check_file_exists(self, file_name, add_cwd=False):
        if add_cwd:
            return os.path.isfile(os.path.join(os.getcwd(), file_name))
        return os.path.isfile(file_name)

    def delete_files(self, starts_with="", ends_with="", file_is=""):
        for i in [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]:
            if starts_with or ends_with:
                if i.startswith(starts_with) and i.endswith(ends_with):
                    os.remove(i)
            if file_is:
                if i == file_is:
                    os.remove(i)

    def bulk_file_select(self, path="", starts_with="", ends_with="", file_is=""):
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

    def select_file(self, message="", full_path=False, files=[]):
        while True:
            if message:
                print(message)
            print("Select a file:")
            if not files:
                files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
            for num, file in enumerate(files, start=1):
                print("{}: {}".format(num, file))
            choice = input("Enter corresponding number to file: ")
            try:
                choice = int(choice)
            except:
                print("Enter a number.")
                continue
            if choice < 1 or choice > len(files):
                print("Make a choice from 1 - {}".format(str(len(files))))
                continue
            if full_path:
                return "{}\\{}".format(os.getcwd(), files[choice - 1])
            return files[choice - 1]

class file_process():
    def __init__(self, file_name):
        self.file_name = file_name

    def unzip(self, extract_dir):
        with zipfile.ZipFile(self.file_name, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

class logger():
    def log(self, message, file_name, sev=5, debug=False):
        try:
            log_level = logging.INFO if not debug else logging.DEBUG
            logging.basicConfig(filename=file_name, level=log_level, format="%(asctime)s:%(levelname)s:%(message)s", datefmt='%Y-%m-%d %H:%M:%S')
            logging.critical(message) if sev == 1 else logging.error(message) if sev == 2 else logging.warning(message) if sev == 3 else logging.info(message) if sev == 4 else logging.debug(message)
            return True
        except:
            return False

if __name__ == '__main__':
    pass