'''
An elasticsearch query pass-through.
Has auth control, so it is better than exposing your ES index directly.
'''

import json, urllib.parse

from flask import Blueprint, request, abort, make_response
from flask_login import current_user

import portality.models as models
from portality.core import app
import portality.util as util


blueprint = Blueprint('query', __name__)


# pass queries direct to index. POST only for receipt of complex query objects
@blueprint.route('/<path:path>', methods=['GET','POST'])
@blueprint.route('/', methods=['GET','POST'])
@util.jsonp
def query(path='Record'):
    pathparts = path.strip('/').split('/')
    subpath = pathparts[0]
    if subpath.lower() in app.config.get('NO_QUERY_VIA_API',[]) and ( current_user.is_anonymous or not current_user.view_admin ):
        abort(401)
    
    if subpath.lower() in ["student", "everything"] and ( current_user.is_anonymous or not current_user.view_admin):
        abort(401)
        
    klass = getattr(models, subpath[0].capitalize() + subpath[1:] )
    
    if len(pathparts) > 1 and pathparts[1] == '_mapping':
        resp = make_response( json.dumps(klass().mapping()) )
    elif len(pathparts) == 2 and pathparts[1] not in ['_mapping','_search']:
        if request.method == 'POST':
            abort(401)
        else:
            rec = klass().pull(pathparts[1])
            if rec:
                resp = make_response( rec.json )
            else:
                abort(404)
    else:
        if request.method == "POST":
            if request.json:
                qs = request.json
            else:
                qs = dict(request.form).keys()[-1]
        elif 'q' in request.values:
            qs = {'query': {'query_string': { 'query': request.values['q'] }}}
        elif 'source' in request.values:
            qs = json.loads(urllib.parse.unquote(request.values['source']))
        else: 
            qs = ''
        for item in request.values:
            if item not in ['q','source','callback','_'] and isinstance(qs,dict):
                if item == 'sort' and '.keyword' not in request.values[item]:
                    if '.exact' in request.values[item]:
                        qs[item] = request.values[item].replace('.exact','.keyword')
                    elif ':' in request.values[item]:
                        qs[item] = request.values[item].replace(':','.keyword:')
                    elif ',' in request.values[item]:
                        qs[item] = request.values[item].replace(',','.keyword,')
                    else:
                        qs[item] = request.values[item] + '.keyword'
                else:
                    qs[item] = request.values[item]
        resp = make_response( json.dumps(klass().query(q=qs)) )
    resp.mimetype = "application/json"
    return resp

