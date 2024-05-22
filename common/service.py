from functools import wraps
import jwt
from common.database import db
from flask import g,request


def change_tenant(schema_name):
    tenant = g.schema = schema_name.sname
    db.choose_tenant(tenant)


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token :
            return "There is no token"
        try:
            data=jwt.decode(token,'vrushabh@2611',algorithms=["HS256"])
            current_user = data['password']
            if current_user is None:
                return "invalid token"
        except Exception as e:
            return str(e)
        return f(current_user,args,kwargs)
    return decorated
