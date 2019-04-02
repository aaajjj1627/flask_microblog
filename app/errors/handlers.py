#encoding:utf-8
from flask import render_template
from app import db
from app.errors import bp

#使blueprint独立于应用
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'),404

@bp.app_errorhandler(505)
def internam_error(error):
    db.session.rollback()
    return render_template('errors/500.html'),500