from flask import Blueprint, render_template, request, redirect

bp = Blueprint('pages', __name__)
curr_file = None


@bp.route('/')
def grid():
    from . import files
    from markupsafe import Markup

    fm = files.FileManager(curr_file)
    td = Markup(files.build_tree())

    return render_template('pages/base_grid.html',
                           tree_data=td, row_data=Markup(fm.get_data()), header_data=Markup(fm.get_header()),
                           current_file=curr_file)


@bp.route('/load_file', methods=['POST'])
def load_file():
    global curr_file
    file = request.form.get('file_to_load', 'empty?')
    curr_file = file
    print(file)
    return redirect('/')


def contact():
    return render_template('pages/base_contact.html')


@bp.route('/about')
def about():
    return render_template('pages/base_about.html')


@bp.route('/tree')
def tree():
    from . import files
    from markupsafe import Markup
    td = Markup(files.build_tree())
    return render_template('pages/base_tree.html', tree_data=td)
