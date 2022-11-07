from flask import render_template,session, request,redirect,url_for,flash
from shop import app,db,bcrypt
from .forms import RegistrationForm,LoginForm
from .models import User
from shop.products.models import Addproduct,Category,Specification

@app.route('/admin')
def admin():
    products = Addproduct.query.all()
    return render_template('admin/index.html', title='Admin page',products=products)

@app.route('/specifications')
def specifications():
    specifications = Specification.query.order_by(Specification.id.desc()).all()
    return render_template('admin/specification.html', title='specifications',specifications=specifications)

@app.route('/categories')
def categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/specification.html', title='categories',categories=categories)

@app.route('/admin/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'{form.email.data} has logged in to the admin panel','success')
            return redirect(url_for('admin'))
        else:
            flash(f'Incorrect email or password', 'success')
            return redirect(url_for('login'))
    return render_template('admin/login.html',title='Login page',form=form)