from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from cache_setup import cache

# Helper function for checking admin
def _check_admin(claims):
    if claims.get('role') != 'admin':
        return {'msg': 'Admin access required'}, 403
    return None


# Dashboard Summary

class AdminSummaryAPI(Resource):
    @jwt_required()
    @cache.cached(timeout=2, key_prefix='admin_summary')
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        data = {
            'total_students': StudentProfile.query.count(),
            'total_companies': CompanyProfile.query.count(),
            'total_drives': PlacementDrive.query.count(),
            'total_applications': Application.query.count(),
            'pending_companies': CompanyProfile.query.filter_by(approval_status='pending').count(),
            'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
            'selected_students': Application.query.filter_by(status='selected').count(),
        }
        return {'summary': data}, 200

# Admin Statistics
class AdminStatisticsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error
            
        return {
            "students": StudentProfile.query.count(),
            "companies": CompanyProfile.query.count(),
            "drives": PlacementDrive.query.count()
        }, 200


# Viewing all students
class AdminStudentsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        students = StudentProfile.query.all()
        result = []
        for s in students:
            d = s.to_dict()
            user = User.query.get(s.user_id)
            if user:
                d['username'] = user.username
                d['email'] = user.email
                d['is_active'] = user.is_active
            result.append(d)
        return {'students': result}, 200


# Viewing all companies
class AdminCompaniesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        companies = CompanyProfile.query.all()
        result = []
        for c in companies:
            d = c.to_dict()
            user = User.query.get(c.user_id)
            if user:
                d['username'] = user.username
                d['email'] = user.email
                d['is_active'] = user.is_active
            result.append(d)
        return {'companies': result}, 200


# Viewing all drives
class AdminDrivesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
        result = []
        for d in drives:
            dd = d.to_dict()
            dd['application_count'] = Application.query.filter_by(drive_id=d.id).count()
            result.append(dd)
        return {'drives': result}, 200


# Viewing all users 
class AdminUsersAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        role_filter = request.args.get('role')
        query = User.query
        if role_filter:
            query = query.filter_by(role=role_filter)

        users = query.order_by(User.created_at.desc()).all()
        result = []
        for u in users:
            d = u.to_dict()
            if u.role == 'company' and u.company_profile:
                d['approval_status'] = u.company_profile.approval_status
            result.append(d)    # Includes status of company
        return {'users': result}, 200


# Searching all users, companies, and students
class AdminSearchAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        q = request.args.get('q', '').strip()
        if not q:
            return {'results': []}, 200

        pattern = f'%{q}%'
        users = User.query.filter(
            (User.username.ilike(pattern)) | (User.email.ilike(pattern))
        ).all()
        companies = CompanyProfile.query.filter(CompanyProfile.company_name.ilike(pattern)).all()
        students = StudentProfile.query.filter(StudentProfile.name.ilike(pattern)).all()

        return {
            'results': {
                'users': [u.to_dict() for u in users],
                'companies': [c.to_dict() for c in companies],
                'students': [s.to_dict() for s in students],
            }
        }, 200


# Pending companies
class PendingCompaniesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error    
        companies = CompanyProfile.query.filter_by(approval_status='pending').all()
        return {'companies': [c.to_dict() for c in companies]}, 200


# Pending drives
class PendingDrivesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error
        drives = PlacementDrive.query.filter_by(status='pending').all()
        return {'drives': [d.to_dict() for d in drives]}, 200


# All applications
class AdminApplicationsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error
        apps = Application.query.order_by(Application.applied_at.desc()).all()
        return {'applications': [a.to_dict() for a in apps]}, 200


# Approve/Reject Company
class ApproveCompanyAPI(Resource):
    @jwt_required()
    def put(self, company_id):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        profile = CompanyProfile.query.get(company_id)
        if not profile:
            return {'msg': 'Company not found'}, 404

        action = request.get_json().get('action', '').lower()
        if action not in ('approved', 'rejected'):
            return {'msg': 'Action must be approved or rejected'}, 400

        profile.approval_status = action
        db.session.commit()
        cache.delete('admin_summary')

        return {'msg': f'Company {action}', 'profile': profile.to_dict()}, 200


# Approve/Reject Drive
class ApproveDriveAPI(Resource):
    @jwt_required()
    def put(self, drive_id):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return {'msg': 'Drive not found'}, 404

        action = request.get_json().get('action', '').lower()
        if action not in ('approved', 'rejected', 'closed'):
            return {'msg': 'Action must be approved, rejected or closed'}, 400

        drive.status = action
        db.session.commit()
        cache.delete('admin_summary')
        cache.delete('approved_drives')

        return {'msg': f'Drive {action}', 'drive': drive.to_dict()}, 200


# Blacklist / Restore User
class BlacklistAPI(Resource):
    @jwt_required()
    def put(self, user_id):
        claims = get_jwt()
        error = _check_admin(claims)
        if error:
            return error

        user = User.query.get(user_id)
        if not user or user.role == 'admin':
            return {'msg': 'User not found or cannot blacklist admin'}, 404

        action = request.get_json().get('action', 'blacklist')

        if user.role == 'company' and user.company_profile:
            is_blacklisting = (action == 'blacklist')
            user.company_profile.is_blacklisted = is_blacklisting

# Closing all active drives of this company
            if is_blacklisting:
                active_drives = PlacementDrive.query.filter(
                    PlacementDrive.company_id == user.company_profile.id,
                    PlacementDrive.status.in_(['pending', 'approved'])
                ).all()
                for drive in active_drives:
                    drive.status = 'closed'

# Cancelling all pending applications for this drive
                    apps = Application.query.filter(
                        Application.drive_id == drive.id,
                        Application.status.notin_(['selected', 'rejected', 'cancelled'])
                    ).all()
                    for a in apps:
                        a.status = 'cancelled'

# Blacklisting student
        elif user.role == 'student' and user.student_profile:
            user.student_profile.is_blacklisted = (action == 'blacklist')

# Deactivating or reactivating user account
        user.is_active = (action != 'blacklist')
        db.session.commit()
        cache.delete('admin_summary')
        cache.delete('approved_drives')

        status_text = 'blacklisted' if action == 'blacklist' else 'restored'
        return {'msg': f'User {status_text}'}, 200