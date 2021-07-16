from flask import Flask, request, render_template, redirect, url_for
from flask import json , render_template
from configs.base_config import Development, Staging
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Staging)



class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    category = db.Column(db.String(), nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

     # fetch all records from database 
    @classmethod
    def fetch_records(cls):
        products = cls.query.all()
        return products

    # fetch records id
    @classmethod
    def fetch_by_id(cls,id):
        record = cls.query.filter_by(id=id)    
        return record

    # create record 
    @classmethod
    def create_record(self):
        db.session.add(self)
        db.session.commit()

    # update by id
    @classmethod
    def update_by_id(cls,id, name, category, buying_price, selling_price, stock_quantity):
        record = cls.query.filter_by(id=id).first()

        if record:

            record.name == name
            record.category == category
            record.buying_price == buying_price
            record.selling_price == selling_price
            record.stock_quantity == stock_quantity
            db.session.add(record)
            db.session.commit()
            return record.name
        else:
            return False

class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key = True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Float, nullable=False)
    date_sold = db.Column(db.DateTime, nullable=False, default=datetime.now)



# create all tables
@app.before_first_request
def create_tables():
    db.create_all()
    print("hello")



  
# conn = psycopg2.connect("dbname=kiosk user=postgres port=5433 password=12345") #connection to local db
conn = psycopg2.connect(dbname="d5c04cvapeivr1", host="ec2-79-125-30-28.eu-west-1.compute.amazonaws.com", user="ruusozkswdaiez", port=5432,  password="c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b") #connection to heroku db
cur = conn.cursor()

# cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, name VARCHAR NOT NULL, buying_price NUMERIC NOT NULL, selling_price NUMERIC NOT NULL, stock_quantity NUMERIC NOT NULL, category VARCHAR NOT NULL);")
# cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY, product_id INTEGER NOT NULL, quantity_sold NUMERIC NOT NULL, date_sold TIMESTAMP );")


@app.route('/base') #displays the base html content
def base():
    return render_template('base.html')

@app.route('/')
def home():
    username = "Mohamed's I-M-S"
    users = ['Peter', 'Jane', 'Joe', 'Mark']
    age  = 25
    return render_template('index.html', usr=username, usrs=users, age=age)

@app.route('/dashboard')
def dashboard():
    cur.execute("SELECT COUNT(*) FROM products;")
    inv = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM sales;")
    sls = cur.fetchone()
    cur.execute("SELECT category,COUNT(*) FROM products GROUP BY category ;")
    pie = cur.fetchall()
    cur.execute("SELECT name,sum(quantity_sold) FROM sales INNER JOIN products ON products.id = sales.product_id GROUP BY name ;")
    bar = cur.fetchall()
    print(bar)

    bar_labels = []
    bar_values = []
    for b in bar:
        bar_labels.append(b[0])
        bar_values.append(int(b[1]))

    pie_labels = []
    pie_values = []

    for x in pie:
       pie_labels.append(x[0])
       pie_values.append(x[1]) 

    print(bar_labels)
    print(bar_values)
    return render_template('dashboard.html',inv=inv,sls=sls, pie_labels=pie_labels,pie_values=pie_values,bar_labels=bar_labels,bar_values=bar_values)

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

#inventory with ID
@app.route('/inventories/<inventory_id>')
def single_inventories(inventory_id):
    return "inventories with ID page" + inventory_id

@app.route('/sales', methods=['POST','GET'])
def sales():
    # cur.execute("SELECT sales.id, product_id, quantity_sold, date_sold, name, selling_price*quantity_sold as total_sales FROM sales INNER JOIN products ON products.id = sales.product_id;")
    # d = cur.fetchall()
    sales = Sale.query.all()

    print(sales)
    return render_template('sales.html',sales=sales)

@app.route('/users')
def users():
    return render_template('users.html')    

@app.route('/users/<int:id>')
def user_id(id):
    return 'users id' +" "+ str(id)  

@app.route('/users/<string:username>')
def user_name(username):
    return f'usersname {username}' 

@app.route('/stock') #stock
def stock():
    return render_template('stock.html')