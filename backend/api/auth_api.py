from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token
from models import db, User, CompanyProfile, StudentProfile

# User login and authentication
class LoginAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return {'msg': 'Username and password are required'}, 400

        user = User.query.filter_by(username=username).first()

        if not user or user.password != password:
            return {'msg': 'Invalid credentials'}, 401

        # Checking if account is active (not blacklisted)
        if not user.is_active:
            return {'msg': 'Your account has been deactivated'}, 403

        token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'user_id': user.id}
        )

        return {'access_token': token, 'role': user.role, 'user_id': user.id}, 200


# Registering User
class RegisterAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', '').strip().lower()

        if not username or not email or not password:
            return {'msg': 'Username, email and password are required'}, 400

        if role not in ('company', 'student'):
            return {'msg': 'Role must be company or student'}, 400

        # Checking if username or email already exists
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            return {'msg': 'Username or email already exists'}, 409

        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.flush()

        if role == 'company':
            profile = CompanyProfile(
                user_id=user.id,
                company_name=data.get('company_name', username),
                hr_contact=data.get('hr_contact', ''),
                website=data.get('website', ''),
                description=data.get('description', ''),
                approval_status='pending'
            )
            db.session.add(profile)
        else:
            profile = StudentProfile(
                user_id=user.id,
                name=data.get('name', username),
                branch=data.get('branch', ''),
                cgpa=float(data.get('cgpa', 0)),
                year=int(data.get('year', 1))
            )
            db.session.add(profile)

        db.session.commit()
        return {'msg': f'{role.title()} registered successfully'}, 201
