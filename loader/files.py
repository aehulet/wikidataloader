import os
import json
from .utils import catch_err

HOME_DIR = os.getcwd()


class FileManager:
    """loads csv files off disk and returns object with formatted
    JSON structures to use with AG Grid control."""
    rows = None
    columns = None
    good_format = False
    header = None
    header_list = []
    data = None

    def __init__(self, filename):
        try:
            self.filename = filename
            self.filepath = get_file_path(filename)
            with open(self.filepath, 'r') as f:
                loaded = self.load_data(f)
                if not loaded:
                    f.close()
                    raise Exception('Application was unable correctly process the selected file.')
        except Exception as e:
            catch_err(e, 'FileManager.init')

    def load_data(self, f):
        """Loads csv data into header and data properties of FileManager object."""
        try:
            dat = f.readlines()
            header_loaded = False
            head_list = []
            line_dict = {}
            line_list = []
            for line in dat:
                if not header_loaded:
                    if line.split(',').__len__() >= 1:
                        head = line.split(',')
                        for i in head:
                            head_list.append({"field": i})
                    else:
                        raise Exception('Selected file has insufficient columns.')
                    header_loaded = True
                    self.header = json.dumps(head_list)
                    self.header_list = head
                    self.columns = head.__len__()
                else:
                    vals = line.split(',')
                    for pos in range(self.columns):
                        line_dict[self.header_list[pos]] = vals[pos]
                    line_list.append(line_dict)
                    line_dict = {}

            self.rows = line_list.__len__()
            if self.rows > 0:
                self.good_format = True
                self.data = json.dumps(line_list)
                return True
            else:
                raise Exception('The selected file has no data rows.')
        except Exception as e:
            catch_err(e, 'FileManager.load_data')
            return False

    def get_data(self):
        return self.data

    def get_header(self):
        return self.header


class Fso:
    def __init__(self, fso_name):
        self.name = fso_name
        self.full_path = HOME_DIR + '/' + self.name
        self.is_dir = os.path.isdir(self.full_path)


def list_files(directory):
    """lists all files and subdirectories in a directory"""
    try:
        fso_list = []
        if directory == 'files':  # controlled root of tree
            full_path = HOME_DIR + '/' + directory
        else:
            full_path = HOME_DIR + '/files/' + directory

        if not os.path.isdir(full_path):
            raise ValueError(f"{full_path} is not a valid directory")

        for o in os.listdir(full_path):
            fso_list.append(Fso(o))
        return fso_list
    except ValueError as v:
        print(v)
        return []


def build_tree():
    import json
    top_list = list_files('files')
    struct = []
    for fso in top_list:
        d = {'text': fso.name, 'icon': "jstree-folder"}
        local_list = list_files(fso.name)
        targ_list = []
        for li in local_list:
            targ_list.append({"text": li.name, "icon": "jstree-file"})
        d['children'] = targ_list
        struct.append(d)

    return json.dumps(struct)


def get_file_path(filename):
    for root, dirs, files in os.walk(HOME_DIR + '/files'):
        if filename in files:
            return os.path.join(root, filename)
