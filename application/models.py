from datetime import datetime
from application import db
from application import app


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # 其他用户字段...


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 货号
    product_id = db.Column(db.String(64), unique=True, nullable=False)
    # 商品名称
    name = db.Column(db.String(128), nullable=False)
    # 尺码
    size = db.Column(db.Integer, default=0)
    # 单价
    price = db.Column(db.Float, nullable=False)
    # 数量
    number = db.Column(db.Integer, nullable=False)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(64), db.ForeignKey("products.product_id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    member_phone = db.Column(db.Integer, db.ForeignKey("members.member_phone"), nullable=False)

    # 外键约束
    product = db.relationship('Products', backref=db.backref('sale', lazy=True))
    member = db.relationship('Members', backref=db.backref('member', lazy=True))


class Members(db.Model):
    member_phone = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(128), nullable=False)
    integral = db.Column(db.Integer, nullable=False)


class Returned(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(64), db.ForeignKey("products.product_id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
