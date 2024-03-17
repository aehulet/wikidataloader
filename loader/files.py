import os
import json
import csv
from .utils import catch_err

HOME_DIR = os.getcwd()


class FileManager:
    """loads csv files off disk and returns object with formatted
    JSON structures to use with AG Grid control."""
    rows = None
    columns = None
    good_format = False
    header_json = None
    header_list = []
    data_json = None
    data_list = []
    outputs_added = False
    initialized = False
    meta_dict = None

    def __init__(self, filename):
        try:
            self.filename = filename
            self.filepath = get_file_path(filename)
            if not self.filepath:
                raise Exception(f'Application was unable to locate {self.filename}.')
            self.initialized = True
        except Exception as e:
            catch_err(e, 'FileManager.init')

    def get_folder(self):
        if self.initialized:
            return os.path.dirname(self.filepath).split('/').pop()
        else:
            return None

    def load_data(self):
        """Loads csv data into header and data properties of FileManager object."""
        try:
            if self.filepath:
                has_header = csv.Sniffer().has_header(self.filepath)
                if has_header:
                    cols = []
                    rows = 0
                    row_dict = {}
                    row_list = []
                    with open(self.filepath) as f:
                        reader = csv.reader(f, delimiter=',')
                        for row in reader:
                            if len(row) > 0:
                                if not self.header_json:
                                    for column in row:
                                        cols.append({'field': column})
                                    self.header_json = json.dumps(cols)
                                    self.header_list = row
                                    total_cols = len(self.header_list)
                                    if row[1][-6:] == '_value':
                                        self.outputs_added = True
                                else:
                                    # self.data_list.append(row)  # save list structure for later
                                    for pos in range(total_cols):
                                        row_dict[self.header_list[pos]] = row[pos]
                                    row_list.append(row_dict)
                                    row_dict = {}
                                    rows += 1

                        self.rows = rows
                        self.good_format = True
                        self.data_json = json.dumps(row_list)

                        self.init_metadata()

                        return True
                else:
                    raise Exception(f'{self.filepath} does not have a header row.')
            else:
                raise Exception('Application was unable to locate the file.')
        except Exception as e:
            catch_err(e, 'FileManager.load_data')
            return False

    def init_metadata(self):
        """loads json file into dictionary, or adds columns data to dictionary if not done yet."""
        the_file = self.get_folder() + '.json'
        the_full_path = get_file_path(the_file)
        try:
            with open(the_full_path, 'r') as j:
                the_dict = json.load(j)

            col_set = the_dict['columns']
            if not col_set:
                col_count = 1
                for column in self.header_list:
                    nm = 'col' + str(col_count)
                    inner_dict = {'name': column, 'instance_of': '', 'property': '', 'literal': False, 'ignore': False}
                    list_tuple = [(nm, inner_dict)]
                    the_dict['columns'].update(list_tuple)
                    col_count += 1

                    self.columns = col_count
                    with open(the_full_path, 'w') as k:
                        k.write(json.dumps(the_dict, indent=4))

            self.meta_dict = the_dict
            self.columns = the_dict['columns'].__len__()
            return True

        except Exception as e:
            catch_err(e, 'FileManager.init_metadata')
            return False

    def write_metadata(self):
        """Writes the meta_dict dictionary to json file."""
        the_file = self.get_folder() + '.json'
        the_full_path = get_file_path(the_file)
        json_str = json.dumps(self.meta_dict, indent=4)
        try:
            with open(the_full_path, 'w') as j:
                j.write(json_str)
                return True
        except Exception as e:
            catch_err(e, "FileManager.write_metadata")
            return False

    def replace_meta_dict(self, json_as_dict):
        """Receives json-as-dict from web page and updates self.meta_dict."""
        self.meta_dict = json_as_dict
        return True

    def update_meta_dict(self, key, value_dict):
        """Updates a particular property in self.meta_dict."""
        try:
            self.meta_dict[key] = value_dict
        except Exception as e:
            catch_err(e, "FileManager.update_meta_dict")
            return False

    def write_data(self, data):
        """takes new json data from grid and writes it to file."""
        self.data_json = data
        try:
            with open(self.filepath, 'w') as f:
                dw = csv.DictWriter(f, fieldnames=self.header_list)  # handles header row in file
                dw.writeheader()
                for row in self.data_json:
                    dw.writerow(row)
            return True
        except Exception as e:
            catch_err(e, 'FileManager.save_data')
            return False

    def add_output_columns(self):
        """Adds one output column for every existing column in the initial csv file.
        Can only be run once."""
        # 1. from self.header_list add to new header list
        try:
            if not self.outputs_added:
                new_head = []
                orig_cols = len(self.header_list)
                # print(len(self.header_list))
                for pos in range(orig_cols):
                    new_head.append(self.header_list[pos])
                    new_head.append(self.header_list[pos] + '_value')
                # 2. from self.data_list add to new data list
                new_data_list = []
                new_data_row = []
                curr_data_list = self.get_data_list()
                curr_data_rows = curr_data_list['result']
                if not curr_data_rows:
                    raise Exception(curr_data_list['error'])
                for row in curr_data_rows:
                    for pos in range(orig_cols):
                        new_data_row.append(row[pos])
                        new_data_row.append('')
                    new_data_list.append(new_data_row)
                    new_data_row = []
                # 3. open file for write; use csv writer
                with open(self.filepath, 'w') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    # 4. write new  header list
                    writer.writerow(new_head)
                    # 5. write new data list
                    for row in new_data_list:
                        writer.writerow(row)

                return True
            else:
                raise Exception('Output columns have already been added')

        except Exception as e:
            catch_err(e, 'FileManager.add_output_columns')
            return False

    def get_data(self):
        return self.data_json

    def set_data(self, data):
        self.data_json = data

    def get_metadata_json(self):
        return json.dumps(self.meta_dict)

    def get_data_list(self):
        import json
        try:
            new_row = []
            the_list = []
            data_dict = json.loads(self.data_json)
            for row in data_dict:
                for k, v in row.items():
                    new_row.append(v)
                the_list.append(new_row)
                new_row = []

            return {'result': the_list, 'error': None}

        except Exception as e:
            err = catch_err(e, 'FileManager.set_data_list')
            return {'result': None, 'error': err}

    def get_header(self):
        return self.header_json

    def set_header(self, header):
        self.header_json = header


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


def write_header_to_file(filename, header):
    try:
        the_file = get_file_path(filename)
        if the_file:
            with open(the_file, 'r') as f:
                data = f.readlines()
                data[0] = header + '\n'

            with open(the_file, 'w') as g:
                g.writelines(data)

            return True
        else:
            print(f"Could not locate {the_file}.")
            return False
    except Exception as e:
        catch_err(e, 'files.write_header_to_file')
        return False


def process_new_file(file_blob):
    import shutil

    try:
        # get names
        filename = file_blob.filename
        filedir = HOME_DIR + '/files/' + filename.split('.')[0]
        # make directory & save file
        os.makedirs(filedir, exist_ok=True)
        file_blob.save(filedir + '/' + filename)  # werkzeug file object method
        # copy json file to target directory
        new_json = filedir + '/' + filename.split('.')[0] + '.json'
        shutil.copy(HOME_DIR + '/stock.json', new_json)

        return True

    except Exception as e:
        catch_err(e, 'files.process_new_file')
        return False


def add_output_columns(filename):
    """Creates an output column for each existing column in a new file. Must be initiated
    by the user and can only be done once."""
    filepath = get_file_path(filename)

    with open(filepath) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            pass
            # 1) add new header entries based on name of input rows; header names of output rows should automatically
            # update if paired input row is updated.
            # 2) iterate across rows, adding a column every other
