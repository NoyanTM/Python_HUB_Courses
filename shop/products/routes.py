from flask import render_template,session, request,redirect,url_for,flash,current_app
from shop import app,db,photos, search
from .models import Category,Specification,Addproduct
from .forms import Addproducts
import secrets
import os

def specifications():
    specifications = Specification.query.join(Addproduct, (Specification.id == Addproduct.specification_id)).all()
    return specifications

def categories():
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/')
def home():
    return render_template("home.html", title="Home")

@app.route('/market')
def market():
    page = request.args.get('page',1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products,specifications=specifications(),categories=categories())

@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name','desc'] , limit=6)
    return render_template('products/result.html',products=products,specifications=specifications(),categories=categories())

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html',product=product,specifications=specifications(),categories=categories())

@app.route('/specification/<int:id>')
def get_specification(id):
    page = request.args.get('page',1, type=int)
    get_specification = Specification.query.filter_by(id=id).first_or_404()
    specification = Addproduct.query.filter_by(specification=get_specification).paginate(page=page, per_page=8)
    return render_template('products/index.html',specification=specification,specifications=specifications(),categories=categories(),get_specification=get_specification)

@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page',1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=8)
    return render_template('products/index.html',get_cat_prod=get_cat_prod,specifications=specifications(),categories=categories(),get_cat=get_cat)

@app.route('/addspecification',methods=['GET','POST'])
def addspecification():
    if request.method =="POST":
        getspecification = request.form.get('specification')
        specification = Specification(name=getspecification)
        db.session.add(specification)
        flash(f'The specification "{getspecification}" was added to website','success')
        db.session.commit()
        return redirect(url_for('addspecification'))
    return render_template('admin/addspecification.html', title='Add Specification',specifications='specifications')

@app.route('/updatespecification/<int:id>',methods=['GET','POST'])
def updatespecification(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    updatespecification = Specification.query.get_or_404(id)
    specification = request.form.get('specification')
    if request.method =="POST":
        updatespecification.name = specification
        flash(f'The specification was changed to "{specification}"','success')
        db.session.commit()
        return redirect(url_for('specifications'))
    specification = updatespecification.name
    return render_template('admin/addspecification.html', title='Update Specification',specifications='specifications',updatespecification=updatespecification)

@app.route('/deletespecification/<int:id>', methods=['GET','POST'])
def deletespecification(id):
    specification = Specification.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(specification)
        flash(f'The specification "{specification.name}" was deleted from website','success')
        db.session.commit()
        return redirect(url_for('specifications'))
    flash(f'The specification "{specification.name}" cannot be deleted from website','warning')
    return redirect(url_for('specifications'))

@app.route('/addcat',methods=['GET','POST'])
def addcat():
    if request.method =="POST":
        getcat = request.form.get('category')
        category = Category(name=getcat)
        db.session.add(category)
        flash(f'The category "{getcat}" was added to website','success')
        db.session.commit()
        return redirect(url_for('addcat'))
    return render_template('admin/addspecification.html', title='Add Category')

@app.route('/updatecat/<int:id>',methods=['GET','POST'])
def updatecat(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')  
    if request.method =="POST":
        updatecat.name = category
        flash(f'The category was changed to "{category}"','success')
        db.session.commit()
        return redirect(url_for('categories'))
    category = updatecat.name
    return render_template('admin/addspecification.html', title='Update Category',updatecat=updatecat)

@app.route('/deletecat/<int:id>', methods=['GET','POST'])
def deletecat(id):
    category = Category.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(category)
        flash(f'The category "{category.name}" was deleted from website','success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f'The category "{category.name}" cannot be deleted from your database','warning')
    return redirect(url_for('admin'))

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    form = Addproducts(request.form)
    specifications = Specification.query.all()
    categories = Category.query.all()
    if request.method=="POST"and 'image_1' in request.files:
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        editions = form.editions.data
        desc = form.discription.data
        specification = request.form.get('specification')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(name=name,price=price,discount=discount,stock=stock,editions=editions,desc=desc,category_id=category,specification_id=specification,image_1=image_1,image_2=image_2,image_3=image_3)
        db.session.add(addproduct)
        flash(f'The course "{name}" was added to website','success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin/addproduct.html', form=form, title='Add Course', specifications=specifications,categories=categories)

@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    form = Addproducts(request.form)
    product = Addproduct.query.get_or_404(id)
    specifications = Specification.query.all()
    categories = Category.query.all()
    specification = request.form.get('specification')
    category = request.form.get('category')
    if request.method =="POST":
        product.name = form.name.data 
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data 
        product.editions = form.editions.data
        product.desc = form.discription.data
        product.category_id = category
        product.specification_id = specification
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        flash(f'The course "{product.name}" was successfully updated','success')
        db.session.commit()
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.editions.data = product.editions
    form.discription.data = product.desc
    specification = product.specification.name
    category = product.category.name
    return render_template('admin/addproduct.html', form=form, title='Update course',getproduct=product, specifications=specifications,categories=categories)

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method =="POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The course "{product.name}" was deleted from website','success')
        return redirect(url_for('admin'))
    flash(f'Cannot delete the course','success')
    return redirect(url_for('admin'))