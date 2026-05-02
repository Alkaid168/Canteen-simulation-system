from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash

from models import Student, AdminUser

# 创建蓝图对象
auth_bp = Blueprint('auth_bp', __name__)


# 学生登录核验
@auth_bp.route('/student/login', methods=['POST'])
def student_login():
    data = request.get_json(silent=True) or {}
    student_id = data.get('student_id', '').strip()
    password = data.get('password', '')

    student = Student.query.filter_by(student_id=student_id).first()
    if not student or not check_password_hash(student.password_hash, password):
        return jsonify(success=False, error='认证失败'), 401
    
    session['student_id'] = student.student_id
    return jsonify(success=True, data={
        'id': student.id,
        'student_id': student.student_id,
        'name': student.name,
    })


# 管理员登录核验
@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    admin = AdminUser.query.filter_by(username=username).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify(success=False, error='认证失败'), 401

    session['admin_username'] = admin.username
    return jsonify(success=True, data={'username': admin.username})


# 退出登录
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify(success=True, data={})