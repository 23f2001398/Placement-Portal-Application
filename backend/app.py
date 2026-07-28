from flask import Flask, send_from_directory
from models import db, User
from api.auth_api import LoginAPI, RegisterAPI
from api.company_api import CompanyProfileAPI, CompanyApplicantsAPI, ApplicationStatusAPI, ScheduleInterviewAPI
from api.student_api import StudentProfileAPI, ResumeUploadAPI, ResumeDownloadAPI, StudentApplicationsAPI, StudentHistoryAPI, ExportCSVAPI, ExportStatusAPI, StudentAppliedDrivesAPI
from api.drive_api import DriveAPI, DriveDetailAPI, MyDrivesAPI, DriveSearchAPI, CompanySearchAPI
from api.application_api import ApplicationAPI, ApplicationDetailAPI
from api.summary_api import AdminSummaryAPI, AdminStudentsAPI, AdminCompaniesAPI, AdminDrivesAPI, AdminUsersAPI, AdminSearchAPI, PendingCompaniesAPI, PendingDrivesAPI, AdminApplicationsAPI, ApproveCompanyAPI, ApproveDriveAPI, BlacklistAPI, AdminStatisticsAPI
from cache_setup import cache
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta
from celery_setup import celery, make_celery
from flask_cors import CORS
from flask_mail import Mail


base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "instance", "ppa.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ppa-secret-key"
app.config["JWT_SECRET_KEY"] = "jwt-ppa-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379'
app.config['CACHE_DEFAULT_TIMEOUT'] = 2

# MailHog Configuration
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_DEFAULT_SENDER'] = 'admin@ppa.com'


db.init_app(app)
cache.init_app(app)
mail = Mail()
mail.init_app(app)
api = Api(app)
jwt = JWTManager(app)
app.app_context().push()

celery.conf.update(
    broker_url="redis://localhost:6379/1",
    result_backend="redis://localhost:6379/2",
    timezone='Asia/Kolkata'
)

_celery_with_app = make_celery(app)
_celery_with_app.conf.update(celery.conf)
celery.__class__ = _celery_with_app.__class__
celery.Task = _celery_with_app.Task
celery.conf = _celery_with_app.conf

from tasks import *


os.makedirs(os.path.join(base_dir, 'instance'), exist_ok=True)  # for database
os.makedirs(os.path.join(base_dir, 'uploads'), exist_ok=True)   # for resumes


def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(username='admin', email='admin@ppa.com', password='admin123', role='admin', is_active=True)
        db.session.add(new_admin)
        db.session.commit()
        return "Admin created"


# Authentication routes
api.add_resource(LoginAPI, '/api/auth/login')
api.add_resource(RegisterAPI, '/api/auth/register')

# Company routes
api.add_resource(CompanyProfileAPI, '/api/company/profile')
api.add_resource(CompanyApplicantsAPI, '/api/company/applicants/<int:drive_id>')
api.add_resource(ApplicationStatusAPI, '/api/company/application/<int:app_id>')
api.add_resource(ScheduleInterviewAPI, '/api/company/schedule-interview/<int:app_id>')

# Student routes
api.add_resource(StudentProfileAPI, '/api/student/profile')
api.add_resource(ResumeUploadAPI, '/api/student/upload-resume')
api.add_resource(ResumeDownloadAPI, '/api/student/resume')
api.add_resource(StudentApplicationsAPI, '/api/student/applications')
api.add_resource(StudentHistoryAPI, '/api/student/history')
api.add_resource(ExportCSVAPI, '/api/student/export-csv')
api.add_resource(ExportStatusAPI, '/api/student/export-status/<task_id>')
api.add_resource(StudentAppliedDrivesAPI, '/api/student/applied-drives')

# Drive routes
api.add_resource(DriveAPI, '/api/drives')
api.add_resource(DriveDetailAPI, '/api/drives/<int:drive_id>')
api.add_resource(MyDrivesAPI, '/api/drives/my')
api.add_resource(DriveSearchAPI, '/api/drives/search')
api.add_resource(CompanySearchAPI, '/api/drives/companies/search')

# Application routes
api.add_resource(ApplicationAPI, '/api/applications')
api.add_resource(ApplicationDetailAPI, '/api/applications/<int:app_id>')

# Admin routes
api.add_resource(AdminSummaryAPI, '/api/admin/summary')
api.add_resource(AdminStudentsAPI, '/api/admin/students')
api.add_resource(AdminCompaniesAPI, '/api/admin/companies')
api.add_resource(AdminDrivesAPI, '/api/admin/drives')
api.add_resource(AdminUsersAPI, '/api/admin/users')
api.add_resource(AdminSearchAPI, '/api/admin/search')
api.add_resource(PendingCompaniesAPI, '/api/admin/pending-companies')
api.add_resource(PendingDrivesAPI, '/api/admin/pending-drives')
api.add_resource(AdminApplicationsAPI, '/api/admin/applications')
api.add_resource(ApproveCompanyAPI, '/api/admin/approve-company/<int:company_id>')
api.add_resource(ApproveDriveAPI, '/api/admin/approve-drive/<int:drive_id>')
api.add_resource(BlacklistAPI, '/api/admin/blacklist/<int:user_id>')
api.add_resource(AdminStatisticsAPI, '/api/admin/statistics')

# Resume route for viewing resume of applicants by company
@app.route('/api/resume/<filename>')
def serve_resume(filename):
    return send_from_directory(os.path.join(base_dir, 'uploads'), filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True, port=5000)