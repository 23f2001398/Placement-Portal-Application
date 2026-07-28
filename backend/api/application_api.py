import os
from datetime import datetime
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.utils import secure_filename
from models import db, Application, PlacementDrive, StudentProfile, CompanyProfile

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')

# Student applications to placement drives
class ApplicationAPI(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'msg': 'Student role required'}, 403

        profile = StudentProfile.query.filter_by(user_id=claims['user_id']).first()
        if not profile:
            return {'msg': 'Student profile not found'}, 404

        if profile.is_blacklisted:
            return {'msg': 'Your account has been blacklisted'}, 403

        if request.content_type and 'multipart' in request.content_type:
            drive_id = request.form.get('drive_id', type=int)
        else:
            data = request.get_json() or {}
            drive_id = data.get('drive_id')

        if not drive_id:
            return {'msg': 'drive_id is required'}, 400

        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return {'msg': 'Drive not found'}, 404

        if drive.status != 'approved':
            return {'msg': 'This drive is not open for applications'}, 400

        if drive.deadline and drive.deadline < datetime.utcnow():
            return {'msg': 'Application deadline has passed'}, 400

        company = CompanyProfile.query.get(drive.company_id)
        if company and company.is_blacklisted:
            return {'msg': 'This company has been blacklisted'}, 400

        if drive.eligibility_cgpa and (profile.cgpa or 0) < drive.eligibility_cgpa:
            return {'msg': f'Minimum CGPA required: {drive.eligibility_cgpa}'}, 400

        if drive.eligibility_year and (profile.year or 0) < drive.eligibility_year:
            return {'msg': f'Minimum year required: {drive.eligibility_year}'}, 400

        if drive.eligibility_branch:
            allowed = [b.strip().lower() for b in drive.eligibility_branch.split(',')]
            if (profile.branch or '').lower() not in allowed and 'all' not in allowed:
                return {'msg': 'Your branch is not eligible for this drive'}, 400

        # Checking duplicate application
        existing = Application.query.filter_by(student_id=profile.id, drive_id=drive_id).first()
        if existing:
            return {'msg': 'You have already applied to this drive'}, 409

        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename and file.filename.lower().endswith('.pdf'):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(f'resume_{profile.id}_{int(datetime.utcnow().timestamp())}.pdf')
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                profile.resume_path = filename

        application = Application(student_id=profile.id, drive_id=drive_id, status='applied')
        db.session.add(application)
        db.session.commit()
        return {'msg': 'Application submitted', 'application': application.to_dict()}, 201


# Fetching details of a specific application
class ApplicationDetailAPI(Resource):
    @jwt_required()
    def get(self, app_id):
        claims = get_jwt()

        application = Application.query.get(app_id)
        if not application:
            return {'msg': 'Application not found'}, 404

        if claims.get('role') == 'student':
            profile = StudentProfile.query.filter_by(user_id=claims['user_id']).first()
            if not profile or application.student_id != profile.id:
                return {'msg': 'Not authorised'}, 403

        elif claims.get('role') == 'company':
            comp_profile = CompanyProfile.query.filter_by(user_id=claims['user_id']).first()
            if not comp_profile:
                return {'msg': 'Not authorised'}, 403
            drive = PlacementDrive.query.get(application.drive_id)
            if not drive or drive.company_id != comp_profile.id:
                return {'msg': 'Not authorised'}, 403

        elif claims.get('role') != 'admin':
            return {'msg': 'Not authorised'}, 403
        return {'application': application.to_dict()}, 200