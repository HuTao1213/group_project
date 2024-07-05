from flask import Blueprint, render_template, request, flash
from application.models import Products, db, app

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET', 'POST'])
def query_products():
    if request.method == 'POST':
        query_type = request.form.get('query_type')
        product_id = request.form.get('product_id')
        name = request.form.get('name')
        size = request.form.get('size')

        query = Products.query

        if query_type == 'zero_inventory':
            query = query.filter_by(number=0)
        elif query_type == 'condition':
            if product_id:
                query = query.filter_by(product_id=product_id)
            if name:
                query = query.filter_by(name=name)
            if size:
                query = query.filter_by(size=size)

        products = query.all()
        if not products:
            flash('没有找到符合条件的商品')

        return render_template('search.html', products=products)

    return render_template('search.html')
