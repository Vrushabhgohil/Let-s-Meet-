from functools import wraps
from flask import g, request
from flask_sqlalchemy import SQLAlchemy

class MultiTenantSQLAlchemy(SQLAlchemy):
    def choose_tenant(self, bind_key):
        g.tenant = bind_key

    def get_engine(self, app=None, bind=None):
        if bind is None:
            if 'tenant' not in g:
                raise RuntimeError('No tenant chosen.')
            bind = g.tenant
        return super().get_engine(app=app, bind=bind)

def switch_tenant(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant = request.headers.get('tenant')
        if tenant:
            g.tenant = tenant
        else:
            g.tenant = None  
        return f(*args, **kwargs)
    return decorated_function

db = MultiTenantSQLAlchemy()