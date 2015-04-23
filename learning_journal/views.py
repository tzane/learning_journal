from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid.security import forget, remember
from pyramid.security import authenticated_userid
from .forms import LoginForm
from .models import User

from .models import (
    Session,
    DBSession,
    MyModel,
    Entry,
    )

from .forms import EntryCreateForm

@view_config(route_name='journal', renderer='templates/list.jinja2')
def journal_page(request):
    entries = Entry.all()
    return {'entries': entries}


@view_config(route_name='home', renderer='templates/list.jinja2')
def show_list_of_entries(request):
    form = None
    if not authenticated_userid(request):
        form = LoginForm()
    return {'entries': Entry.all(), 'login_form': form}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def view(request):
    this_id = request.matchdict.get('id', -1)
    entry = Entry.by_id(this_id)
    if not entry:
        return HTTPNotFound()
    return {'entry': entry}


@view_config(route_name='create', renderer='templates/edit.jinja2', permission='create')
def create(request):
    entry = Entry()
    form = EntryCreateForm(request.POST)
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        session = Session()
        session.add(entry)
        session.commit()
        #return HTTPFound(location=request.route_url('home'))
        return HTTPFound(location=request.route_url('detail', id=entry.id))
    return {'form': form, 'action': 'create'}


@view_config(route_name='edit', renderer='templates/edit.jinja2', permission='create')
def update(request):
    entry_id = request.matchdict['id']
    entry = Entry.by_id(entry_id)
    if not entry:
        return HTTPNotFound()
    form = EntryCreateForm(request.POST)
    if request.method == 'GET':
        form.title.data = entry.title
        form.body.data = entry.body
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        #return HTTPFound(location=request.route_url('home'))
        return HTTPFound(location=request.route_url('detail', id=entry.id))
    return { 'form': form, 'action': 'edit' }
    
# @view_config(route_name='auth', match_param='action=in', renderer='string', request_method='POST')
# def sign_in(request):
    # login_form = None
    # if request.method == 'POST':
        # login_form = LoginForm(request.POST)
    # if login_form and login_form.validate():
        # user = User.by_name(login_form.username.data)
        # if user and user.verify_password(login_form.password.data):
            # headers = remember(request, user.name)
        # else:
            # headers = forget(request)
    # else:
        # headers = forget(request)
    # return HTTPFound(location=request.route_url('home'), headers=headers)
  
@view_config(route_name='login', renderer='string', request_method='POST')
def sign_in(request):
    login_form = None
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
    if login_form and login_form.validate():
        user = User.by_name(login_form.username.data)
        if user and user.has_password(login_form.password.data):
            headers = remember(request, user.name)
        else:
            headers = forget(request)
    else:
        headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)
  
conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

