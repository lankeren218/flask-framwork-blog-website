# _*_coding:utf-8_*_
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
# 上下文处理器能让变量在所有模板中全局可访问，从而不用再每个render_template()中都添加模板参数
# 截止第九章还没用到这个，后面再看
