from operator import or_
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask import json , render_template
from sqlalchemy.orm import backref, lazyload
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.functions import func
from configs.base_config import Development, Staging
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy 
import psycopg2
from datetime import datetime
from functools import wraps
# from flask_moment import Moment

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Staging)
# moment = Moment(app)
print("World")

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    category = db.Column(db.String(), nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    # This is a one to many relationship
    # A product can have many sales related
    sale = db.relationship('Sale', backref='product', lazy='dynamic')

class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key = True)
    #product_id = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Float, nullable=False)
    date_sold = db.Column(db.DateTime, nullable=False, default=datetime.now())
    # Connect sale to the product that was sold 
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    confirm_password = db.Column(db.String, nullable=False)
    # reg_date = db.Column(db.DateTime, default=datetime.utcnow())



# create all tables
@app.before_first_request
def create_tables():
    db.create_all()
    

  
# conn = psycopg2.connect("dbname=kiosk user=postgres port=5433 password=12345") #connection to local db
conn = psycopg2.connect(dbname="d5c04cvapeivr1", host="ec2-79-125-30-28.eu-west-1.compute.amazonaws.com", user="ruusozkswdaiez", port=5432,  password="c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b") #connection to heroku db
cur = conn.cursor()

# cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, name VARCHAR NOT NULL, buying_price NUMERIC NOT NULL, selling_price NUMERIC NOT NULL, stock_quantity NUMERIC NOT NULL, category VARCHAR NOT NULL);")
# cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY, product_id INTEGER NOT NULL, quantity_sold NUMERIC NOT NULL, date_sold TIMESTAMP );")


@app.route('/login', methods=['POST','GET'])
def login():
    
    if request.method == 'POST':
        session.pop('user_id', None) # drops session before request is made

        email = request.form['email']
        password = request.form['password'] 

        user = User.query.filter_by(email = email).first()
        if user:
            if user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('home'))
            flash('Invalid Username or Password') 
            return redirect(url_for('login'))
        flash('email does not exist')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/')

def home():
    age = 30
    # super_user = User(id=1, first_name='Mohamed', last_name='Jumale', email='mohamed@qiyaas.com', password='admin1234', confirm_password='admin1234')
    return render_template('index.html', age=age)
    

@app.route('/dashboard')
def dashboard():
    products = Product.query.count()

    sales = Sale.query.count()

    categories = Product.query.with_entities(Product.category, func.count()).group_by(Product.category).all()

    pie_labels = []
    pie_values = []
    for label, value in categories:
        pie_labels.append(label)
        pie_values.append(value)

    
    sale_per_item = Sale.query.with_entities(Product.name, func.sum(Sale.quantity_sold)).join(Product).group_by(Product.name).all()

    bar_labels = []
    bar_values = []
    for label, value in sale_per_item:
        bar_labels.append(label)
        bar_values.append(value)
    
    # cur.execute("SELECT COUNT(*) FROM products;")
    # inv = cur.fetchone()
    # cur.execute("SELECT COUNT(*) FROM sales;")
    # sls = cur.fetchone()
    # cur.execute("SELECT category,COUNT(*) FROM products GROUP BY category ;")
    # pie = cur.fetchall()
    # cur.execute("SELECT name,sum(quantity_sold) FROM sales INNER JOIN products ON products.id = sales.product_id GROUP BY name ;")
    # bar = cur.fetchall()
    # print(bar)

    # bar_labels = []
    # bar_values = []
    # for b in bar:
    #     bar_labels.append(b[0])
    #     bar_values.append(int(b[1]))

    # pie_labels = []
    # pie_values = []
    # for x in categories:
    #    pie_labels.append(x[0])
    #    pie_values.append(x[1]) 

    return render_template('dashboard.html',products=products,sales=sales, pie_labels=pie_labels,pie_values=pie_values,bar_labels=bar_labels,bar_values=bar_values)

@app.route('/inventories',methods=['POST','GET'])
def inventories():
    if request.method == "GET":
        # cur.execute("SELECT * FROM products;")
        # x = cur.fetchall()
        # all_products = Product.fetch_records()
        all_products = Product.query.all()
        print(all_products)
        return render_template('inventories.html', all_products=all_products )
    else:
        name = request.form['name']
        stock_quantity = request.form['stock_quantity']
        buying_price = request.form['buying_price']
        selling_price = request.form['selling_price']
        category = request.form['category']
        
        new_product = Product(name=name, stock_quantity=stock_quantity, buying_price=buying_price, selling_price=selling_price, category=category)

        db.session.add(new_product)
        db.session.commit()
        print(new_product)

        # print(n,b,s,q,c)
        # cur.execute("INSERT INTO products (name, stock_quantity, buying_price, selling_price,category) VALUES (%s, %s, %s, %s, %s)", (n,q,b,s,c))
        # conn.commit()
        return redirect(url_for('inventories'))

@app.route('/make_sale', methods=['POST','GET']) #is accessed when sale button is clicked in inventories template
def make_sale():
    if request.method == 'GET':
        
        return redirect(url_for('sales'))
    else:  
        pid = request.form['product_id']
        qt = request.form ['stock_quantity']

        print(pid,qt)

        # cur.execute("UPDATE products SET stock_quantity =%s WHERE id= %s ", (qt,pid))
        # cur.execute("INSERT INTO sales (product_id, quantity_sold, date_sold) VALUES (%s,%s,'NOW()')", (pid,qt))
        # conn.commit()
        item_selected = Sale(product_id=pid,quantity_sold=qt)
        db.session.add(item_selected)
        db.session.commit()
        print(item_selected)
    

        return redirect(url_for('sales'))

@app.route('/edit_inventory/<int:id>', methods=['POST','GET'])
def edit(id):

    if request.method == 'POST':
        record = Product.query.filter_by(id=id).first()

        record.name = request.form['name']
        record.buying_price = request.form['buying_price']
        record.selling_price = request.form['selling_price']
        record.stock_quantity = request.form['quantity']
        record.category = request.form['category']

        db.session.add(record)
        db.session.commit()

        print('Record successfully added', record.name)
        # cur.execute('UPDATE products SET name = %s, buying_price = %s, selling_price = %s, stock_quantity = %s, category = %s WHERE products.id = %s ;',(nm,bp,sp,q,c,id))
        # conn.commit()
        return redirect(url_for('inventories'))
    else:
        record_by_id = Product().fetch_by_id(id=id)


        return render_template('inventories.html')

@app.route('/delete_inventory/<int:id>', methods = ['POST','GET'])
def delete_inventory(id):

    if request.method == 'GET':
        return render_template('inventories.html')

    id = request.form['id']
    
    record = Product.query.filter_by(id=id).first()
    

    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('inventories'))

#inventory with ID
@app.route('/inventories/<inventory_id>')
def single_inventories(inventory_id):
    return "inventories with ID page" + inventory_id

@app.route('/sales', methods=['POST','GET'])
def sales():
    # cur.execute("SELECT sales.id, product_id, quantity_sold, date_sold, name, selling_price*quantity_sold as total_sales FROM sales INNER JOIN products ON products.id = sales.product_id;")
    # d = cur.fetchall()
    sales = db.session.query(Product, Sale).join(Sale).all()
    
    return render_template('sales.html',sales=sales)

@app.route('/users')
def users():
    all_users = User.query.all()

    return render_template('users.html',all_users=all_users)    

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'GET':
        return render_template('users.html')
    
    first_name = request.form['f_name']
    last_name = request.form['l_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    user_check = User.query.filter_by(email=email).first()
    
    if user_check.email==request.form['email']:
        
        return redirect(url_for('users'))

    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, confirm_password=confirm_password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('users'))

@app.route('/users/<int:id>')
def user_id(id):
    return 'users id' +" "+ str(id)  

@app.route('/users/<string:username>')
def user_name(username):
    return f'usersname {username}' 

@app.route('/stock') #stock
def stock():
    return render_template('stock.html')