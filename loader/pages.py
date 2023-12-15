from flask import Blueprint, render_template, request, redirect

bp = Blueprint('pages', __name__)


@bp.route('/')
def grid():
    return render_template('pages/base_grid.html')


@bp.route('/about')
def about():
    return render_template('pages/base_about.html')


@bp.route('/tree')
def tree():
    from . import files
    from markupsafe import Markup
    td = Markup(files.build_tree())
    return render_template('pages/base_tree.html', tree_data=td)
