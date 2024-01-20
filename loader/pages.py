from flask import Blueprint, render_template, request, redirect
from .utils import catch_err
import json

bp = Blueprint('pages', __name__)
curr_file = 'Select a file to open.'
selected = False
node_id = ''
good_write = True
err_message = ''


@bp.route('/')
def grid():
    from . import files
    from markupsafe import Markup
    global good_write, err_message
    head = Markup('{}')
    rows = Markup('{}')
    select_json = Markup(json.dumps({"selected": "None"}))
    node_json = Markup(json.dumps({"node_id": "None"}))
    outputs_added_json = Markup(json.dumps({"outputs": "None"}))
    num_columns = Markup(json.dumps({"num_columns": "None"}))
    metadata = None
    err_msg = err_message
    err_message = ''
    try:
        td = Markup(files.build_tree())
        fm = files.FileManager(curr_file)
        if selected:
            select_json = Markup(json.dumps({"selected": curr_file}))
            node_json = Markup(json.dumps({"node_id": node_id}))

        if not good_write:
            good_write = True
            raise Exception('The file update process failed. Please try again, reload, or reimport the file.')

        if fm.filepath:
            fm.load_data()
            if fm.good_format:
                head = Markup(fm.get_header())
                rows = Markup(fm.get_data())
                outputs_added_json = Markup(json.dumps({"outputs": fm.outputs_added}))
                metadata = Markup(fm.get_metadata_json())
                num_columns = Markup(fm.columns)
        else:
            if selected:
                raise Exception('There is a problem with the location or format of this file.')

        return render_template('pages/base_grid.html', tree_data=td,
                               current_file=curr_file, node_json=node_json, select_json=select_json,
                               row_data=rows, header_data=head, outputs_added=outputs_added_json,
                               metadata=metadata, num_columns=num_columns, err_msg=err_msg)
    except Exception as e:
        err_msg = str(e)
        catch_err(e, 'pages.grid')
        return render_template('pages/base_grid.html', tree_data=td,
                               current_file=curr_file, node_json=node_json, select_json=select_json,
                               row_data=rows, header_data=head, outputs_added=outputs_added_json, err_msg=err_msg)


@bp.route('/load_file', methods=['POST'])
def load_file():
    global curr_file, selected, node_id
    file = request.form.get('file_to_load', 'empty?')
    node_id = request.form.get('node_id')
    curr_file = file
    selected = True
    return redirect('/')


@bp.route('/write_file', methods=['POST'])
def write_file():
    from .files import FileManager
    global good_write
    fm = FileManager(curr_file)
    fm.load_data()
    good_write = fm.write_data(request.get_json())

    return redirect('/')


@bp.route('/write_metadata', methods=['POST'])
def write_metadata():
    from .files import FileManager
    global good_write, selected
    fm = FileManager(curr_file)
    fm.load_data()
    selected = True
    good_write = fm.write_metadata(request.get_json())

    return redirect('/')


@bp.route('/new_file', methods=['POST'])
def upload_new_file():
    from .files import process_new_file
    global curr_file, err_message
    try:
        fileblob = request.files['new_file']
        if not fileblob.filename == '':
            process_new_file(fileblob)
            curr_file = fileblob.filename
        else:
            raise Exception('No file selected')

        return redirect('/')

    except Exception as e:
        catch_err(e, 'pages.upload_new_file')
        err_message = str(e)
        return redirect('/')


@bp.route('/add_outputs', methods=['POST'])
def add_output_columns():
    from .files import FileManager
    global curr_file, err_message
    try:
        fm = FileManager(curr_file)
        fm.load_data()
        if not fm.add_output_columns():
            err_message = 'The output columns could not be added.'
        return redirect('/')

    except Exception as e:
        err_message = catch_err(e, 'pages.add_output_columns')

        return redirect('/')


@bp.route('/reload_me', methods=['POST', 'GET'])
def reload_me():
    print('redirecting to root...')
    return redirect('/')


@bp.route('/contact')
def contact():
    return render_template('pages/base_contact.html')


@bp.route('/about')
def about():
    return render_template('pages/base_about.html')


@bp.route('/tree')
def tree():
    return render_template('pages/base_tree.html')
