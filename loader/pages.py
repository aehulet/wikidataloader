from flask import Blueprint, render_template, request, redirect

bp = Blueprint('pages', __name__)
curr_file = None


@bp.route('/')
def grid():
    from . import files
    from markupsafe import Markup

    if curr_file:
        print(f'Current file: {curr_file}')

    td = Markup(files.build_tree())
    return render_template('pages/base_grid.html', tree_data=td)


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
