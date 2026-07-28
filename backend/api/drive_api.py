from datetime import datetime
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, PlacementDrive, CompanyProfile, Application
from cache_setup import cache


# Listing approved drives
class DriveAPI(Resource):
    @jwt_required()
    def get(self):
        now = datetime.utcnow()
        expired = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.deadline != None,
            PlacementDrive.deadline < now
        ).all()
        if expired:
            for d in expired:
                d.status = 'closed'
            db.session.commit()
            cache.delete('approved_drives')

        cached = cache.get('approved_drives')
        if cached is not None:
            return cached

        drives = PlacementDrive.query.filter_by(status='approved').order_by(PlacementDrive.created_at.desc()).all()
        result = {'drives': [d.to_dict() for d in drives]}, 200
        cache.set('approved_drives', result, timeout=2)
        return result

    @jwt_required()
    def post(self):
        claims = get_jwt()

        if claims.get('role') != 'company':
            return {'msg': 'Company role required'}, 403

        profile = CompanyProfile.query.filter_by(user_id=claims['user_id']).first()
        if not profile:
            return {'msg': 'Company profile not found'}, 404

        if profile.approval_status != 'approved':
            return {'msg': 'Your company must be approved by admin first'}, 403

        if profile.is_blacklisted:
            return {'msg': 'Your company has been blacklisted'}, 403

        data = request.get_json()
        if not data or not data.get('job_title'):
            return {'msg': 'job_title is required'}, 400

        drive = PlacementDrive(
            company_id=profile.id,
            job_title=data.get('job_title', ''),
            description=data.get('description', ''),
            eligibility_branch=data.get('eligibility_branch', ''),
            eligibility_cgpa=float(data.get('eligibility_cgpa', 0)),
            eligibility_year=int(data.get('eligibility_year', 0)),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        cache.delete('approved_drives')

        return {'msg': 'Drive created (pending approval)', 'drive': drive.to_dict()}, 201


# Getting drive details
class DriveDetailAPI(Resource):
    @jwt_required()
    def get(self, drive_id):
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return {'msg': 'Drive not found'}, 404

        data = drive.to_dict()
        data['application_count'] = Application.query.filter_by(drive_id=drive_id).count()
        return {'drive': data}, 200


# Getting same company's drives
class MyDrivesAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'msg': 'Company role required'}, 403

        profile = CompanyProfile.query.filter_by(user_id=claims['user_id']).first()
        if not profile:
            return {'msg': 'Company profile not found'}, 404

        drives = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).all()
        result = []
        for d in drives:
            dd = d.to_dict()
            dd['application_count'] = Application.query.filter_by(drive_id=d.id).count()
            result.append(dd)

        return {'drives': result}, 200


# Searching approved drives
class DriveSearchAPI(Resource):
    @jwt_required()
    def get(self):
        q = request.args.get('q', '').strip()
        branch = request.args.get('branch', '').strip().lower()
        cgpa = request.args.get('cgpa', type=float)
        year = request.args.get('year', type=int)

        query = PlacementDrive.query.filter_by(status='approved')
        # Filtering by job title and description
        if q:
            pattern = f'%{q}%'
            query = query.filter(
                (PlacementDrive.job_title.ilike(pattern)) |
                (PlacementDrive.description.ilike(pattern))
            )

        # Filtering by year eligibility
        if year:
            query = query.filter(
                (PlacementDrive.eligibility_year == None) |
                (PlacementDrive.eligibility_year == 0) |
                (PlacementDrive.eligibility_year == year)
            )

        # Filtering by CGPA eligibility
        if cgpa is not None:
            query = query.filter(
                (PlacementDrive.eligibility_cgpa == None) |
                (PlacementDrive.eligibility_cgpa <= cgpa)
            )

        drives = query.order_by(PlacementDrive.created_at.desc()).all()

        # Filtering by branch
        if branch:
            filtered = []
            for d in drives:
                if not d.eligibility_branch:
                    filtered.append(d)
                    continue
                allowed = [b.strip().lower() for b in d.eligibility_branch.split(',')]
                if 'all' in allowed or branch in allowed:
                    filtered.append(d)
            drives = filtered

        return {'drives': [d.to_dict() for d in drives]}, 200


# Searching companies
class CompanySearchAPI(Resource):
    @jwt_required()
    def get(self):
        q = request.args.get('q', '').strip()
        if not q:
            return {'companies': []}, 200

        pattern = f'%{q}%'
        companies = CompanyProfile.query.filter(
            CompanyProfile.company_name.ilike(pattern),
            CompanyProfile.approval_status == 'approved',
            CompanyProfile.is_blacklisted == False
        ).all()

        return {'companies': [c.to_dict() for c in companies]}, 200