from datetime import datetime
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, CompanyProfile, Application, PlacementDrive

# Helper function for getting company profile
def _get_company_profile(claims):
    if claims.get('role') != 'company':
        return None, ({'msg': 'Company role required'}, 403)
    profile = CompanyProfile.query.filter_by(user_id=claims.get('user_id')).first()
    if not profile:
        return None, ({'msg': 'Company profile not found'}, 404)
    return profile, None


# Company profile operations
class CompanyProfileAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        profile, error = _get_company_profile(claims)
        if error:
            return error
        return profile.to_dict(), 200

    @jwt_required()
    def put(self):
        claims = get_jwt()
        profile, error = _get_company_profile(claims)
        if error:
            return error

        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        profile.company_name = data.get('company_name', profile.company_name)
        profile.hr_contact = data.get('hr_contact', profile.hr_contact)
        profile.website = data.get('website', profile.website)
        profile.description = data.get('description', profile.description)
        db.session.commit()

        return {'msg': 'Profile updated', 'profile': profile.to_dict()}, 200


# List of applicants for a specific drive
class CompanyApplicantsAPI(Resource):
    @jwt_required()
    def get(self, drive_id):
        claims = get_jwt()
        profile, error = _get_company_profile(claims)
        if error:
            return error

        # Checking the drive is for this company or not
        drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first()
        if not drive:
            return {'msg': 'Drive not found or not yours'}, 404

        # Getting all applications for this drive with student details
        apps = Application.query.filter_by(drive_id=drive_id).all()
        result = []
        for a in apps:
            app_data = a.to_dict()
            if a.student:
                app_data['student_name'] = a.student.name
                app_data['student_branch'] = a.student.branch
                app_data['student_cgpa'] = a.student.cgpa
                app_data['student_resume'] = a.student.resume_path
            result.append(app_data)

        return {'applicants': result}, 200


# Updating application status of a student
class ApplicationStatusAPI(Resource):
    @jwt_required()
    def put(self, app_id):
        claims = get_jwt()
        profile, error = _get_company_profile(claims)
        if error:
            return error

        application = Application.query.get(app_id)
        if not application:
            return {'msg': 'Application not found'}, 404

        # Checking this application is for this company's drive or not
        drive = PlacementDrive.query.get(application.drive_id)
        if not drive or drive.company_id != profile.id:
            return {'msg': 'Not authorised to update this application'}, 403

        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        new_status = data.get('status', '').lower()
        if new_status not in ('shortlisted', 'selected', 'rejected'):
            return {'msg': 'Status must be shortlisted, selected or rejected'}, 400

        application.status = new_status
        db.session.commit()

        return {'msg': 'Status updated', 'application': application.to_dict()}, 200


# Scheduling an interview for a shortlisted student
class ScheduleInterviewAPI(Resource):
    @jwt_required()
    def post(self, app_id):
        claims = get_jwt()
        profile, error = _get_company_profile(claims)
        if error:
            return error

        application = Application.query.get(app_id)
        if not application:
            return {'msg': 'Application not found'}, 404

        # Checking this application is for this company's drive or not
        drive = PlacementDrive.query.get(application.drive_id)
        if not drive or drive.company_id != profile.id:
            return {'msg': 'Not authorised to schedule interview for this application'}, 403

        # Checking if the application is shortlisted or not
        if application.status != 'shortlisted':
            return {'msg': 'Only shortlisted students can be scheduled for interview'}, 400

        data = request.get_json()
        if not data:
            return {'msg': 'No data provided'}, 400

        # Getting interview details
        interview_time = data.get('interview_time') or data.get('interview_date')
        interview_mode = data.get('interview_mode', '').lower()
        interview_location = data.get('interview_location', '')

        if not interview_time:
            return {'msg': 'interview_time is required'}, 400

        if interview_mode not in ('online', 'offline'):
            return {'msg': 'interview_mode must be online or offline'}, 400

        # Parsing the date string
        try:
            application.interview_date = datetime.fromisoformat(interview_time)
        except (ValueError, TypeError):
            return {'msg': 'Invalid date format'}, 400

        application.interview_mode = interview_mode
        application.interview_location = interview_location if interview_mode == 'offline' else None
        application.status = 'interview_scheduled'
        db.session.commit()

        return {'msg': 'Interview scheduled', 'application': application.to_dict()}, 200