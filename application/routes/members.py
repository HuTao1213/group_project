from flask import Blueprint, render_template, request, flash, redirect, url_for
from application.models import Members, db, app

members_bp = Blueprint('members', __name__)

@members_bp.route('/members', methods=['GET', 'POST'])
def manage_members():
    if request.method == 'POST':
        member_phone = request.form.get('member_phone')
        name = request.form.get('name')
        sex = request.form.get('sex')
        action = request.form.get('action')

        if not member_phone:
            flash('会员号码不能为空')
            return render_template('members.html')

        member = Members.query.filter_by(member_phone=member_phone).first()

        # 查询
        if action == 'query':
            if member:
                return render_template('members.html', member=member)
            else:
                flash('未找到会员信息')
                return render_template('members.html')
        # 新增
        elif action == 'add':
            if member:
                flash('会员号码已存在')
            else:
                new_member = Members(member_phone=member_phone, name=name, sex=sex, integral=0)
                db.session.add(new_member)
                db.session.commit()
                flash('会员新增成功')
            return redirect(url_for('members.manage_members'))
        # 修改
        elif action == 'update':
            if member:
                member.name = name
                member.sex = sex
                db.session.commit()
                flash('会员信息更新成功')
            else:
                flash('未找到会员信息')
            return redirect(url_for('members.manage_members'))

    return render_template('members.html')
