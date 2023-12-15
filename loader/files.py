import os


HOME_DIR = os.getcwd()


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


def list_files_recursive(path):
    for item in os.listdir(path):
        full_item = os.path.join(path, item)
        if os.path.isdir(full_item):
            print(full_item)
            list_files_recursive(full_item)
        else:
            print(full_item)


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
