# _*_coding:utf-8_*_
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
# 到时候回头看为何没有errors（第七章的main里面有）
