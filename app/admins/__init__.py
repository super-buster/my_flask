# -*- coding: utf-8 -*-
from flask import Blueprint

bp=Blueprint('admins',__name__)


from app.admins import models
from app.admins import routes
