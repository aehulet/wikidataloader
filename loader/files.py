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
            if not self.filepath:
                raise Exception(f'Application was unable to locate {self.filename}.')
        except Exception as e:
            catch_err(e, 'FileManager.init')

    def load_data(self):
        """Loads csv data into header and data properties of FileManager object."""
        try:
            if self.filepath:
                with open(self.filepath) as f:
                    dat = f.readlines()
                    header_loaded = False
                    head_list = []
                    line_dict = {}
                    line_list = []
                    for line in dat:
                        if not header_loaded:
                            if line.split(',').__len__() >= 1:
                                head = line[:-1].split(',')
                                for i in head:
                                    head_list.append({"field": i})
                            else:
                                raise Exception('Selected file has insufficient columns.')
                            header_loaded = True
                            self.header = json.dumps(head_list)
                            self.header_list = head
                            self.columns = head.__len__()
                        else:
                            end = line[len(line) - 1:len(line)]
                            if end == '\n':
                                vals = line[:-1].split(',')
                            else:
                                vals = line[:len(line)].split(',')

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
            else:
                raise Exception(f'Could not open file {self.filepath}.')
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
    the_path = ''
    for root, dirs, files in os.walk(HOME_DIR + '/files'):
        if filename in files:
            the_path = os.path.join(root, filename)
    if the_path == '':
        return False
    else:
        return the_path


def write_grid_to_file(filename, grid):
    try:
        rows = grid.__len__()
        the_file = get_file_path(filename)
        if the_file:
            if rows > 0:
                keys_str = ','.join(grid[0].keys())
                keys_str += '\n'
                with open(the_file, 'w') as f:
                    f.write(keys_str)
                    for g in grid:
                        g_str = ''
                        for k, v in g.items():
                            g_str += v + ','
                        g_str = g_str[:-1] + '' + '\n'
                        f.write(g_str)
                    f.close()
                    return True

            else:
                print("Unable to save empty file.")
                return False
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("File not found")
        return False
    except Exception as e:
        catch_err(e, 'files.write_grid_to_file')
        return False
