from celery_setup import celery
from celery.schedules import crontab
from models import db, User, PlacementDrive, Application, StudentProfile, CompanyProfile, ExportJob
from jinja2 import Template
from datetime import datetime, timedelta
import csv
import os

def create_report(report_date, data):
    with open("report_template.html", "r") as f:
        template = Template(f.read())
        return template.render(report_date=report_date, data=data)

def send_email(to_email, subject, content, attachment=None):
    from app import app, mail
    from flask_mail import Message
    with app.app_context():
        msg = Message(subject=subject, recipients=[to_email], html=content)
        
        if attachment and os.path.exists(attachment):
            with open(attachment, "rb") as f:
                msg.attach(
                    os.path.basename(attachment),
                    "text/csv",
                    f.read()
                )
                
        mail.send(msg)
        print('Email sent to', to_email)
        
        if attachment and os.path.exists(attachment):
            os.remove(attachment)

celery.conf.beat_schedule = {
    'daily reminder': {
        'task': 'tasks.daily_reminder',
        'schedule': 60.0,  # for e.g. only
        # 'schedule': crontab(hour=18, minute=0),  # Every day at 6:00 PM
    },
    'monthly report': {
        'task': 'tasks.monthly_report',
        'schedule': 60.0,   # for e.g. only
        # 'schedule': crontab(day_of_month='1', hour=0, minute=0),  # 1st of every month at midnight
    }
}



@celery.task
def daily_reminder():
    now = datetime.utcnow()
    # Searching drives closing within 2 days
    two_days_from_now = now + timedelta(days=2)
    drives = PlacementDrive.query.filter(PlacementDrive.status == 'approved', PlacementDrive.deadline > now, PlacementDrive.deadline <= two_days_from_now).all()
    
    if not drives:
        return 'No upcoming drives closing soon'
        
    students = StudentProfile.query.all()
    
    for student in students:
        user = User.query.get(student.user_id)
        if user and user.email:
            content = f'<h1>Daily Reminder for {student.name}</h1><p>You have upcoming application deadlines for placement drives closing within 2 days. Apply before they expire!</p>'
            send_email(user.email, 'Upcoming Placement Drives Reminder', content)
            
    print('Daily reminders sent')

@celery.task
def monthly_report():
    admin = User.query.filter_by(role='admin').first()
    if not admin or not admin.email:
        return 'No admin found'

    total_drives = PlacementDrive.query.count()
    total_apps = Application.query.count()
    selected = Application.query.filter_by(status='selected').count()
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()

    data = {
        'total_drives': total_drives,
        'total_applications': total_apps,
        'selected': selected,
        'total_students': total_students,
        'total_companies': total_companies
    }

    report_date = datetime.utcnow().strftime('%B %Y')
    report = create_report(report_date, data)
    
    send_email(admin.email, f'Monthly Report - {report_date}', report)
    
    print('Monthly report sent')

@celery.task
def export_csv(student_id):
    profile = StudentProfile.query.get(student_id)
    if not profile:
        return 'Student not found'
        
    user = User.query.get(profile.user_id)
    apps = Application.query.filter_by(student_id=student_id).all()
    
    if not apps:
        return 'No data to export'
        
    filename = f'export_{student_id}.csv'
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date', 'Interview Date'])
        for a in apps:
            writer.writerow([
                profile.id,
                a.drive.company.company_name if a.drive and a.drive.company else '',
                a.drive.job_title if a.drive else '',
                a.status,
                a.applied_at.strftime('%Y-%m-%d') if a.applied_at else '',
                a.interview_date.strftime('%Y-%m-%d') if a.interview_date else ''
            ])
            
    if user and user.email:
        send_email(user.email, 'Data Export Complete', f'<p>Dear {profile.name},</p><p>Your placement application data has been exported and is attached.</p>', filename)
    
    task_id = export_csv.request.id
    if task_id:
        job = ExportJob.query.filter_by(task_id=task_id).first()
        if job:
            job.status = 'completed'
            db.session.commit()
            
    return 'Export complete'