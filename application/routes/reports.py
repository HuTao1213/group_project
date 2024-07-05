# 明细

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, date
from application.models import Products, Sale, Returned, Members, db, app

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET'])
def view_reports():
    today = date.today()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    total_sales_today = db.session.query(db.func.sum(Sale.total_price)).filter(db.func.date(Sale.timestamp) == today).scalar()
    total_sales_month = db.session.query(db.func.sum(Sale.total_price)).filter(Sale.timestamp >= start_of_month).scalar()
    total_sales_year = db.session.query(db.func.sum(Sale.total_price)).filter(Sale.timestamp >= start_of_year).scalar()
    total_sales_today = total_sales_today or 0
    total_sales_month = total_sales_month or 0
    total_sales_year = total_sales_year or 0

    purchasing_customers_count = Sale.query.count()
    member_customers_count = Sale.query.filter(Sale.member_phone.isnot(None)).count()

    return render_template('reports.html',
                           total_sales_today=total_sales_today,
                           total_sales_month=total_sales_month,
                           total_sales_year=total_sales_year,
                           purchasing_customers_count=purchasing_customers_count,
                           member_customers_count=member_customers_count)

@reports_bp.route('/reports/details', methods=['GET'])
def report_details():
    page = request.args.get('page', 1, type=int)
    sales = Sale.query.paginate(page, 50, False)
    return render_template('report_details_partial.html', sales=sales)

@reports_bp.route('/reports/returns', methods=['POST'])
def process_return():
    product_id = request.form.get('product_id')
    sale = Sale.query.get(product_id)
    if sale:
        returned = Returned(
            product_id=sale.product_id,
            name=sale.name,
            size=sale.size,
            total_price=sale.total_price,
            member_phone=sale.member_phone
        )
        db.session.add(returned)
        db.session.delete(sale)
        db.session.commit()
        flash('退货成功')
    else:
        flash('未找到对应的销售记录')
    return jsonify(success=True)

@reports_bp.route('/reports/returned', methods=['GET'])
def view_returned():
    returned = Returned.query.all()
    return render_template('returned_partial.html', returned=returned)

@reports_bp.route('/reports/summary', methods=['GET'])
def view_summary():
    summary = db.session.query(
        Sale.name,
        db.func.count(Sale.id).label('total_quantity'),
        db.func.sum(Sale.total_price).label('total_sales')
    ).group_by(Sale.name).all()
    return render_template('summary_partial.html', summary=summary)

