from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import and_

from website.models import Client, Root
from flask_login import login_required, logout_user, current_user

database = Blueprint('database', __name__)

#datebase_Add
@database.route('/datebase-Add/<location_id>/<curr_page>', methods = ['GET', 'POST'])
@login_required
def datebase_Add(location_id, curr_page=1):
    if current_user.has_permission('admin'):

      name = request.form.get('search_by_name')
      if name != None:
          curr_page = 1

          clients = Client.query.filter(and_(Client.roots.any(id=int(location_id)), Client.name.startswith(name))).paginate(
              page=int(curr_page), per_page=4)

      else:
          clients = Client.query.filter(Client.roots.any(id = int(location_id))).paginate(
              page=int(curr_page), per_page=4)


      curr_root = Root.query.get(location_id)
      child_roots = Root.query.filter(Root.id_parent == location_id).all()

      return render_template(
          "database_addition.html",
          client_base_exist = Client.query.all() != [],
          clients=clients, user=current_user,
      curr_root= curr_root,
      child_roots = child_roots)
    else:
        logout_user()
        return redirect(url_for('auth.login'))


