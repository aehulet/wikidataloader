import pywikibot as p
import pywikibot.exceptions
import requests
from enum import Enum


site = p.Site('test', 'wikidata')


class Stage(Enum):
    init = 'reconciled'
    add = 'add items'
    update = 'update items'


def get_table(file_path_name):
    """creates list of lists from source file."""
    from os import path
    if path.isfile(file_path_name):
        table = []
        with open(file_path_name, 'r') as dat:
            file_list = dat.readlines()
        for f in file_list:
            r = f.split(',')
            n = r.__len__() - 1
            val = r[n]
            r[n] = val[:val.__len__() - 1]
            table.append(r)
        return table
    else:
        return "That file doesn't exist yet. Make sure to follow the process steps in order."


def write_table(file_path, tbl: list, stage: Stage):
    """Creates table for each stage of the data loading workflow."""

    parts = file_path.split('.')
    if stage == Stage.init:
        new_path = parts[0] + '_reconciled.' + parts[1]
    elif stage == Stage.add:
        new_path = parts[0] + '_items_added.' + parts[1]
    else:  # update stage
        new_path = parts[0] + '_items_updated.' + parts[1]

    with open(new_path, 'w') as f:
        for r in tbl:
            line = ','.join(r)
            f.write(line + '\n')
        f.close()


def check_duplicates(file_path):
    """checks for duplicate item entries"""
    pass


def get_datatypes(file_path):
    """gets datatypes from source file based on file header values"""
    pass


def check_datatypes(file_path):
    """checks datatypes in source file based on results of get_datatypes()"""
    pass


def reconcile_process(file_path_name):
    """Reads each source column value in data file and returns zero or more Q codes with matching
    labels or aliases. """
    table = None
    try:
        table = get_table(file_path_name)
        if isinstance(table, list):
            h = table[0]  # get header row values
            width = h.__len__()
            depth = table.__len__()

            for c in range(0, width - 1, 2):  # move across table, even-numbered columns only
                for r in range(1, depth):  # move down table at curr col, skipping header row.
                    row = table[r]
                    result = get_items(row[c])
                    table[r][c + 1] = result
            write_table(file_path_name, table, Stage.init)
            return print(file_path_name + " successfully reconciled.")
        else:
            return print(table)  # table is formatted error message in this case.
    except Exception as e:
        print(e)
        write_table(file_path_name, table, Stage.init)
        return print("Error processing {}. Address issue and retry.".format(file_path_name))


def get_items(key_phrase: str):
    key_to_use = key_phrase.strip()
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': key_to_use,
        'language': 'en',
        'maxlag': 5
    }
    ids = ''
    try:
        end_point = 'https://test.wikidata.org/w/api.php'
        pgs = requests.get(end_point, params)
        pgs = pgs.json()

        if pgs['search'].__len__() == 0:
            return key_to_use
        else:
            for d in pgs['search']:
                lbl = d['label'].strip()
                if lbl == key_to_use:  # only return exact matches
                    if not ids.__len__() == 0:
                        ids += '|'
                    ids += d['id']
        if ids.__len__() == 0:  # if no results passed exact match test then return key_phrase
            ids = key_to_use
        return ids

    except Exception as e:
        print(e)
        return str(e)


def add_items_process(origin_file):
    table = None
    errors = False
    try:
        name_part = origin_file.split('.')[0]
        table = get_table('{}_reconciled.csv'.format(name_part))
        if isinstance(table, list):
            h = table[0]  # get header row values
            width = h.__len__()
            depth = table.__len__()
            codes = {}  # tracks qcodes generated in session. Used to avoid unwanted dups.

            for c in range(1, width - 1, 2):  # move across table
                for r in range(1, depth):  # move down table at curr col, skipping header row.
                    try:
                        row = table[r]
                        label = row[c].split(':')[0]  # need label only, not label:description
                        keys = codes.keys()
                        if label in keys:  # if key already generated
                            qcode = add_item(codes[label])  # pass the already existing code
                        else:
                            qcode = add_item(row[c])  # pass the string; new code gets generated
                            codes[label] = qcode  # add new qcode to dictionary
                        table[r][c] = qcode
                    except Exception as e:
                        errors = True
                        print(e)
                        table[r][c] = str(e)
            write_table(origin_file, table, Stage.add)
            if errors:
                msg = ("There were errors while processing new items in the reconciliation table. "
                       "Review the updates table for details.")
            else:
                msg = name_part + '_reconciled.csv items successfully added.'
            return print(msg)
        else:
            return table  # table is formatted error str
    except Exception as e:
        print(e)
        write_table(origin_file, table, Stage.add)
        return print("Error processing reconciliation file. Address issue and retry.")


def add_item(label: str):
    if label[:1] == 'Q':
        return label  # add nothing if input is a Qcode - avoid double entry
    else:
        label_data = label.split(":")
        new_item = p.ItemPage(site)
        label_dict = {'en': label_data[0]}
        new_item.editLabels(labels=label_dict, summary="Setting labels")
        if label_data.__len__() > 1:
            new_item.editDescriptions({'en': label_data[1]})
        # Add description here or in another function
        # sleep(2)
        return new_item.getID()


def update_items_process(origin_file):
    table = None
    repo = site.data_repository()
    errors = False
    try:
        name_part = origin_file.split('.')[0]
        table = get_table('{}_items_added.csv'.format(name_part))
        if isinstance(table, list):
            head = table[0]  # get header row values
            width = head.__len__()
            depth = table.__len__()
            for r in range(1, depth):  # move down table by rows.
                row = table[r]
                item_code = row[1]
                item = p.ItemPage(repo, item_code)  # get page for updates
                for c in range(3, width, 2):
                    try:
                        pcode = head[c].split(':')[0]
                        value = row[c]
                        claim = p.Claim(repo, pcode)  # make new claim object
                        # target equals the page for the entity itself represented by the qcode
                        target = p.ItemPage(repo, value)
                        claim.setTarget(target)
                        msg = 'Added {} claim'.format(row[c - 1])  # use the label value, not the qcode
                        item.addClaim(claim, summary=msg)
                        table[r].append(msg)  # create outcome value at end of row/list
                    except Exception as e:
                        errors = True
                        print(e)
                        table[r].append(str(e))
                # sleep(2)  # 5 second pause between item edits
            write_table(origin_file, table, Stage.update)
            if errors:
                msg = ("There were errors while processing the reconciliation table. "
                       "Review the updates table for details.")
            else:
                msg = name_part + '_reconciled.csv items successfully updated.'
            return print(msg)
        else:
            return table  # table is formatted error str in this case
    except Exception as e:
        print(e)
        write_table(origin_file, table, Stage.update)


# if __name__ == '__main__':
    # reconcile_process('files/new_foods.csv')
    # add_items_process('files/new_foods.csv')
    # update_items_process('files/new_foods.csv')
