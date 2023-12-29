from flask import Blueprint, render_template, request, redirect
from .utils import catch_err
import json

bp = Blueprint('pages', __name__)
curr_file = 'Select a file to open.'
selected = False
node_id = ''


@bp.route('/')
def grid():
    from . import files
    from markupsafe import Markup
    head = Markup('{}')
    rows = Markup('{}')
    select_json = Markup(json.dumps({"selected": "None"}))
    node_json = Markup(json.dumps({"node_id": "None"}))
    err_msg = ''

    try:
        if selected:
            select_json = Markup(json.dumps({"selected": curr_file}))
            node_json = Markup(json.dumps({"node_id": node_id}))

        td = Markup(files.build_tree())
        fm = files.FileManager(curr_file)
        if fm.filepath:
            fm.load_data()
            if fm.good_format:
                head = Markup(fm.get_header())
                rows = Markup(fm.get_data())
        else:
            if selected:
                raise Exception('There is a problem with the location or format of this file.')

        return render_template('pages/base_grid.html', tree_data=td,
                               current_file=curr_file, node_json=node_json, select_json=select_json,
                               row_data=rows, header_data=head, err_msg=err_msg)
    except Exception as e:
        err_msg = str(e)
        catch_err(e, 'pages.grid')
        return render_template('pages/base_grid.html', tree_data=td,
                               current_file=curr_file, node_json=node_json, select_json=select_json,
                               row_data=rows, header_data=head, err_msg=err_msg)


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
    from .files import write_grid_to_file
    data = request.get_json()
    print(data)
    write_grid_to_file(curr_file, data)

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
