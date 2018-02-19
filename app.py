from flask import (Flask, render_template, url_for, flash, redirect,
                    render_template, g, request, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_required,
                            current_user, login_user, logout_user)

import models
import forms

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'verysecretkeypsssssst!!!!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/', methods=("GET", "POST"))
@login_required
def index():
    stream = models.Entry.select().where(
    models.Entry.deleted == False).where(
    models.Entry.user == g.user.id).limit(5)
    return render_template('index.html', stream=stream)


@app.route('/new_entry', methods=("GET", "POST"))
@login_required
def new_entry():
    form = forms.NewEntryForm()
    if form.validate_on_submit():
        flash("Your entry has been successfully added!", "success")
        models.Entry.create_entry(
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.what_i_learned.data,
            resources=form.resources_to_remember.data,
            deleted=False,
            tags=form.tags.data,
            user=g.user.id
        )
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/edit/<int:entry_id>', methods=("GET", "POST"))
@login_required
def edit_entry(entry_id):
    entry = models.Entry.select().where(models.Entry.id == entry_id).get()
    form = forms.EditEntryForm()
    if form.validate_on_submit():
        query = models.Entry.select().where(models.Entry.id == entry_id).get()
        query.title = form.title.data
        query.date = form.date.data
        query.time_spent = form.time_spent.data
        query.learned = form.what_i_learned.data
        query.resources = form.resources_to_remember.data
        query.save()
        flash("Your entry '{}' has been successfully updated!".format(query.title), "success")
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, stream=entry)


@app.route('/entries/tags/<tag>', methods=("GET", "POST"))
@login_required
def get_tags(tag):
    query = models.Entry.select().where(
    models.Entry.tags.contains(tag)).where(models.Entry.user == g.user.id)
    return render_template('tags.html', stream=query)


@app.route('/entries/delete/<int:entry_id>', methods=("GET", "POST"))
@login_required
def delete_entry(entry_id):
    try:
        query = models.Entry.select().where(models.Entry.id == entry_id).get()
    except models.DoesNotExist:
        abort(404)
    else:
        flash("Your entry '{}' has been successfully deleted!".format(query.title), "success")
        query.deleted = True
        query.save()
    return redirect(url_for('index'))


@app.route('/entries/recover/<int:entry_id>', methods=("GET", "POST"))
@login_required
def recover_entry(entry_id):
    query = models.Entry.select().where(models.Entry.id == entry_id).get()
    flash("Your entry has been successfully recovered!", "success")
    query.deleted = False
    query.save()
    return redirect(url_for('index'))


@app.route('/entries')
@login_required
def entries():
    try:
        stream = models.Entry.select().where(
        models.Entry.deleted == False).where(
        models.Entry.user == g.user.id).limit(100)
    except models.DoesNotExist:
        abort(404)
    return render_template('entries.html', stream=stream)


@app.route('/entries/<int:entry_id>')
@login_required
def view_entry(entry_id):
    try:
        entries = models.Entry.select().where(models.Entry.id == entry_id).get()
    except models.DoesNotExist:
        abort(404)
    return render_template('detail.html', stream=entries)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username or password does not match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You have been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your username or password does not match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404



if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='admin',
            password='admin',
            admin=True
        )
    except ValueError:
        pass
    try:
        models.User.create_user(
            username='admin2',
            password='admin2',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
