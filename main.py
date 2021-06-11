from flask import Flask, request, render_template, redirect, url_for
from flask import json , render_template
from configs.base_config import Development, Staging
from werkzeug.utils import redirect

app = Flask(__name__)
app.config.from_object(Staging)

import psycopg2  
# conn = psycopg2.connect("dbname=kiosk user=postgres port=5433 password=12345") #connection to local 
conn = psycopg2.connect(dbname="d5c04cvapeivr1", host="ec2-79-125-30-28.eu-west-1.compute.amazonaws.com", user="ruusozkswdaiez", port=5432,  password="c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b") #connection to heroku db
cur = conn.cursor()


@app.route('/base') #displays the base html content
def base():
    return render_template('base.html')

@app.route('/')
def home():
    username = "Techcamp Kenya"
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
        cur.execute("SELECT * FROM products;")
        x = cur.fetchall()
        return render_template('inventories.html',x=x)
    else:
        n = request.form['name']
        q = request.form['stock_quantity']
        b = request.form['buying_price']
        s = request.form['selling_price']
        c = request.form['category']

        print(n,b,s,q,c)
        cur.execute("INSERT INTO products (name, stock_quantity, buying_price, selling_price,category) VALUES (%s, %s, %s, %s, %s)", (n,q,b,s,c))
        conn.commit()
        return redirect(url_for('inventories'))

@app.route('/make_sale', methods=['POST','GET']) #is accessed when sale button is clicked
def make_sale():
    if request.method == 'GET':
        
        return redirect(url_for('sales'))
    else:  
        pid = request.form['product_id']
        qt = request.form ['stock_quantity']

        print(pid,qt)

        cur.execute("UPDATE products SET stock_quantity =%s WHERE id= %s ", (qt,pid))
        cur.execute("INSERT INTO sales (product_id, quantity_sold, date_sold) VALUES (%s,%s,'2021-01-01')", (pid,qt))
        conn.commit()
        return redirect(url_for('sales'))

@app.route('/edit_sales', methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        nm = request.form['name']
        bp = request.form['buying_price']
        sp = request.form['selling_price']
        q = request.form['quantity']
        id = request.form['id']
        c = request.form['category']

        cur.execute('UPDATE products SET name = %s, buying_price = %s, selling_price = %s, stock_quantity = %s, category = %s WHERE products.id = %s ;',(nm,bp,sp,q,c,id))
        conn.commit()
        return redirect(url_for('inventories'))
    else:
        return render_template('inventories.html')

#inventory with ID
@app.route('/inventories/<inventory_id>')
def single_inventories(inventory_id):
    return "inventories with ID page" + inventory_id

@app.route('/sales', methods=['POST','GET'])
def sales():
    cur.execute("SELECT sales.id, product_id, quantity_sold, date_sold, name, selling_price*quantity_sold as total_sales FROM sales INNER JOIN products ON products.id = sales.product_id;")
    d = cur.fetchall()
    print(d)
    return render_template('sales.html',d=d)

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