from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from application.models import Products, Sale, Members, db, app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/sales', methods=['GET', 'POST'])
def manage_sales():
    if 'products' not in session:
        session['products'] = []
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if product_id:
            with app.app_context():
                products = Products.query.filter_by(product_id=product_id).all()
            if products:
                product_info = {
                    'product_id': products[0].product_id,
                    'name': products[0].name,
                    'price': products[0].price,
                    'sizes': [{'size': p.size, 'number': p.number} for p in products]
                }
                session['products'].append(product_info)
                session.modified = True
            else:
                flash('未找到商品信息！')
        else:
            flash('条码为空！')
        return redirect(url_for('sales.manage_sales'))
    return render_template('sales.html', products=session['products'])


@sales_bp.route('/check_member', methods=['POST'])
def check_member():
    member_phone = request.form.get('member_phone')
    if member_phone:
        member = Members.query.filter_by(member_phone=member_phone).first()
        if member:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'message': '会员信息不存在'})
    else:
        return jsonify({'valid': True})


@sales_bp.route('/process_sale', methods=['POST'])
def process_sale():
    member_phone = request.form.get('member_phone')
    total_price = 0
    if 'products' in session:
        with app.app_context():
            for product in session['products']:
                selected_size = request.form.get(f"size_{product['product_id']}")
                quantity = int(request.form.get(f"quantity_{product['product_id']}", 1))
                discount = float(request.form.get(f"discount_{product['product_id']}", 100)) / 100

                db_product = Products.query.filter_by(product_id=product['product_id'], size=selected_size).first()
                if db_product and db_product.number >= quantity:
                    price = product['price'] * discount * quantity
                    total_price += price
                    db_product.number -= quantity

                    sale = Sale(product_id=product['product_id'], name=product['name'], size=selected_size,
                                total_price=price, timestamp=datetime.now(), member_phone=member_phone)
                    db.session.add(sale)
                else:
                    flash(f'商品库存不足：货号 {product["product_id"]} 尺码 {selected_size}')
                    return redirect(url_for('sales.manage_sales'))
            db.session.commit()
            flash(f'收款成功，总价为：{total_price}')
            session.pop('products', None)
    else:
        flash('没有商品信息，无法完成销售！')
    return redirect(url_for('sales.manage_sales'))


@sales_bp.route('/remove_product/<int:index>', methods=['POST'])
def remove_product(index):
    if 'products' in session:
        session['products'].pop(index)
        session.modified = True
    return redirect(url_for('sales.manage_sales'))


@sales_bp.route('/clear_products', methods=['POST'])
def clear_products():
    session.pop('products', None)
    return redirect(url_for('sales.manage_sales'))

@sales_bp.route('/add_sale', methods=['POST'])
def add_sale(product_id):
    product_id=product_id
    name = request.form.get('name')
    price = request.form.get('price')
    sizes = request.form.get('sizes')
    number = request.form.get('number')
    sale=Products(product_id=product_id, name=name, price=price, size=sizes, number=number)
    db.session.add(sale)
    db.session.commit()
    flash("商品录入成功！")
    return redirect(url_for('sales.manage_sales'))

# 批次管理
UPLOAD_FOLDER = '/path/to/upload'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@sales_bp.route('/upload_products', methods=['POST'])
def upload_products():
    if 'file' not in request.files:
        flash('没有文件上传')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('未选择文件')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            data = pd.read_excel(filepath)
            for index, row in data.iterrows():
                product = Products(
                    product_id=row['货号'],
                    name=row['品名'],
                    size=row['尺码'],
                    number=row['数量'],
                    price=row['单价']
                )
                db.session.add(product)
            db.session.commit()
            flash('商品信息已成功导入')
        except Exception as e:
            db.session.rollback()
            flash(f'导入商品信息时发生错误: {e}')
        finally:
            os.remove(filepath)
        return redirect(url_for('sales.manage_sales'))
    else:
        flash('文件格式不支持')
        return redirect(request.url)