import os
from datetime import datetime
from flask_restful import Resource
from flask import request, send_from_directory, make_response
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.utils import secure_filename
from models import db, StudentProfile, Application, ExportJob

# Resume folder
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')


# Helper function for getting student profile
def _get_student_profile(claims):
    if claims.get('role') != 'student':
        return None, ({'msg': 'Student role required'}, 403)
    profile = StudentProfile.query.filter_by(user_id=claims.get('user_id')).first()
    if not profile:
        return None, ({'msg': 'Student profile not found'}, 404)
    return profile, None


# Student Profile
class StudentProfileAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error
        return profile.to_dict(), 200

    @jwt_required()
    def put(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        profile.name = data.get('name', profile.name)
        profile.branch = data.get('branch', profile.branch)
        profile.cgpa = float(data.get('cgpa', profile.cgpa or 0))
        profile.year = int(data.get('year', profile.year or 1))
        db.session.commit()

        return {'msg': 'Profile updated', 'profile': profile.to_dict()}, 200


# Resume
class ResumeUploadAPI(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        if 'resume' not in request.files:
            return {'msg': 'No file part. Use field name "resume"'}, 400

        file = request.files['resume']
        if file.filename == '':
            return {'msg': 'No selected file'}, 400

        if not file.filename.lower().endswith('.pdf'):
            return {'msg': 'Only PDF files are allowed'}, 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(f"resume_{profile.id}_{int(datetime.utcnow().timestamp())}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        profile.resume_path = filename
        db.session.commit()

        return {'msg': 'Resume uploaded successfully', 'filename': filename}, 200


# Downloading resume
class ResumeDownloadAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        if not profile.resume_path:
            return {'msg': 'No resume uploaded yet'}, 404

        return make_response(send_from_directory(UPLOAD_FOLDER, profile.resume_path, as_attachment=True))


# Applications
class StudentApplicationsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        apps = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
        return {'applications': [a.to_dict() for a in apps]}, 200


# History
class StudentHistoryAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        apps = Application.query.filter(
            Application.student_id == profile.id,
            Application.status.in_(['selected', 'rejected', 'cancelled'])
        ).order_by(Application.applied_at.desc()).all()

        return {'history': [a.to_dict() for a in apps]}, 200


# Export CSV
class ExportCSVAPI(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        from tasks import export_csv
        task = export_csv.delay(profile.id)
        job = ExportJob(student_id=profile.id, task_id=task.id, status='pending')
        db.session.add(job)
        db.session.commit()

        return {'msg': 'CSV export started', 'task_id': task.id, 'job_id': job.id}, 202


# Export Status
class ExportStatusAPI(Resource):
    @jwt_required()
    def get(self, task_id):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        job = ExportJob.query.filter_by(task_id=task_id, student_id=profile.id).first()
        if not job:
            return {'msg': 'Export job not found'}, 404

        return {'job': job.to_dict()}, 200


# Applied Drives
class StudentAppliedDrivesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_student_profile(claims)
        if error:
            return error

        apps = Application.query.filter_by(student_id=profile.id).all()
        return {'applied_drive_ids': [a.drive_id for a in apps]}, 200