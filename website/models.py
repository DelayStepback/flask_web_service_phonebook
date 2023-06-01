from random import randint, choice

#from faker import Faker

from website.db_init import db
from flask_login import UserMixin


# def create_fake_users(n, root_id):
#     """Generate fake users."""
#     faker = Faker()
#     for i in range(n):
#         client = Client(name=faker.name(),
#                         number=randint(9999000000, 9999999999),
#                         role=choice(["продавец", "администрация", "покупатель"]),
#                         royalty=choice([0, 1, 2]))
#         db.session.add(client)
#         client.grant_root(root_id)
#     db.session.commit()
#     print(f'Added {n} fake users to the database.')

class User(db.Model, UserMixin):

    # User Authentication information
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def what_permission(self):
        if not self.roles:
            return False
        else:
            return Role.query.filter_by(id =
                                  UserRoles.query.filter_by(user_id = self.id).first().role_id).first().name
    def has_permission(self, name):
        """Check out whether a user has a permission or not."""
        role = Role.query.filter_by(name=name).first()
        # if the permission does not exist or was not given to the user
        if not role or not role in self.roles:
            return False
        return True
    def grant_permission(self, name):
        """Grant a permission to a user."""
        role = Role.query.filter_by(name=name).first()
        if role and role in self.roles:
            return
        if not role:
            role = Role()
            role.name = name
            db.session.add(role)
            db.session.commit()
        self.roles.append(role)
    def revoke_permission(self, name):
        """Revoke a given permission for a user."""
        role = Role.query.filter_by(name=name).first()
        if not role or not role in self.roles:
            return
        self.roles.remove(role)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


# baserole Client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    number = db.Column(db.Integer, index=True)
    role = db.Column(db.String(30))
    royalty = db.Column(db.Integer)

    # Relationships
    roots = db.relationship('Root', secondary='client_root',
                            backref=db.backref('clients', lazy='dynamic'))


    def what_root(self):
        if not self.roots:
            return False
        else:
            return Root.query.filter_by(id =
                                  ClientRoot.query.filter_by(client_id = self.id).first().root_id).first().id
    def has_root(self, location):
        """Check out whether a user has a permission or not."""
        root = Root.query.filter_by(location=location).first()
        # if the permission does not exist or was not given to the user
        if not root or not root in self.roots:
            return False
        return True
    def grant_root(self, id_root):
        """Grant a permission to a user."""
        root = Root.query.get(id_root)
        self.roots.append(root)
    def revoke_root(self, location):
        """Revoke a given permission for a user."""
        root = Root.query.filter_by(location=location).first()
        if not root or not root in self.roots:
            return
        self.roots.remove(root)



class Root(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    location = db.Column(db.String(60))
    id_parent = db.Column(db.Integer())

class ClientRoot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    client_id = db.Column(db.Integer(), db.ForeignKey('client.id', ondelete='CASCADE'))
    root_id = db.Column(db.Integer(), db.ForeignKey('root.id', ondelete='CASCADE'))



