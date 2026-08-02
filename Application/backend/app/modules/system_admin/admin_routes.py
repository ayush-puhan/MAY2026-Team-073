from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import bcrypt

from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.clubs import Club
from app.database.models.events import Event
from app.database.models.support import SupportTicket
from app.database.models.audit import AuditLog
from app.database.models.academics import Department
from app.database.models.university import UniversityDomain, University
from app.database.enums import UserRole, TicketStatus


from app.utils.email import send_email
from app.utils.helpers import save_base64_image,delete_uploaded_file
from app.middleware.auth_middleware import require_auth ,require_role

system_admin_bp = Blueprint('system_admin', __name__)

@system_admin_bp.route('/stats',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def get_admin_stats():
    try:
        with get_session() as db:
            total_users = db.query(User).count()
            active_users = db.query(User).filter_by(is_active = 1).count()
            total_clubs = db.query(Club).count()
            total_evetns = db.query(Event).count()
            open_tickets = db.query(SupportTicket).filter_by(status = TicketStatus.OPEN).count()

    except Exception as e:
        return {"message" : f"Error : {e}"}, 500
    
    return jsonify({
        "totalUsers" : total_users,
        "activeUsers" : active_users,
        "totalClubs" : total_clubs,
        "totalEvents" : total_evetns,
        "openTickets" : open_tickets,
        "userTrend": 5.2,
        "clubTrend": 2.1,
        "eventTrend": 10.5,
        "ticketTrend": -3.0,
        "userTrendDirection": "up",
        "clubTrendDirection": "up",
        "eventTrendDirection": "up",
        "ticketTrendDirection": "down"
    }), 200


@system_admin_bp.route('/audit-logs',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def get_admin_audit_logs():
    try:
        limit = request.args.get("limit", default=10, type=int)
        with get_session() as db:
            audit_logs = db.query(AuditLog).limit(limit).all()
    except Exception as e:
        return {"message" : f"Error : {e}"}, 500
    
    return jsonify([
        {
            "id": audit.id,
            "user_id": audit.user_id,
            "university_id": audit.university_id,
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "details": audit.details
        } for audit in audit_logs
    ]), 200

@system_admin_bp.route('/audit-logs',methods=['POST'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def make_admin_audit_logs():
    # ----------NOT IMPLEMENTED------------
    try : 
        data = request.get_json()
        print(data)
    except Exception as e:
        return { "message" : f"Error : {e}"}, 500
    pass
    
@system_admin_bp.route('/users',methods=['POST'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_create_user():
    try : 
        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        role = data.get('role')
        university_id = data.get('university_id') or None

        password = f"Password@123"
        has_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with get_session() as db:
            existing_user = db.query(User).filter_by(email=email).first()
            if existing_user:
                if existing_user.is_active:
                    return {"message": "User with this email already exists."}, 400
                else:
                    # User exists but not active (abandoned OTP registration), allow overwrite
                    user_to_update = existing_user
                    user_to_update.full_name = full_name
                    user_to_update.password_hash = has_password
                    user_to_update.role = role 
                    user_to_update.university_id = university_id
            else:
                user_to_update = User(
                    email=email,
                    full_name=full_name,
                    password_hash=has_password,
                    role=role,
                    university_id = university_id
                )
                db.add(user_to_update)
            db.commit()
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    
    # Send password email in background
    try:
        import threading
        subject = "Don't Reply : New Accout Created"
        html = f"your email : {email}\n password : {password}"
        threading.Thread(target=send_email, args=(email,subject, html)).start()
    except Exception as e:
        print(f"Background email error: {e}")

    return {"message": "User created successfully", "email": email,"password":password}, 201
    

@system_admin_bp.route('/users',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_get_all_users():
    try : 
        with get_session() as db:
            users = db.query(User).outerjoin(User.department).outerjoin(User.university).all()   
            result = [
                {
                    "id" : user.id,
                    "full_name" : user.full_name,
                    "email" : user.email,
                    "role" : user.role,
                    "is_active" : user.is_active,
                    "created_at" : user.created_at,
                    "university_name" : user.university.name if user.university else None,
                    "department" : user.department.name if user.department else None,
                    "roll_number" : user.roll_number

                } for user in users
            ]              
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    
    return jsonify(result)

@system_admin_bp.route('/users/<int:id>',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_get_by_id(id):
    try : 
        with get_session() as db:
            user = db.query(User).filter_by(id=id).outerjoin(User.department).outerjoin(User.university).first()   
            result = {
                    "id" : user.id,
                    "full_name" : user.full_name,
                    "email" : user.email,
                    "role" : user.role,
                    "is_active" : user.is_active,
                    "created_at" : user.created_at,
                    "university_name" : user.university.name if user.university else None,
                    "department" : user.department.name if user.department else None,
                    "roll_number" : user.roll_number
            }          
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    
    return jsonify(result)


@system_admin_bp.route('/users/<int:id>/status',methods=['PATCH'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_change_status_by_id(id):
    try : 
        data = request.get_json()
        with get_session() as db:
            user = db.query(User).filter_by(id=id).first()   
            user.is_active = data['status']
            db.commit() 
    except Exception as e:
        return { "message" : f"error : {e}"}, 500
    
    return { "message" : "Status Changed."}, 200
    


@system_admin_bp.route('/users/<int:id>',methods=['DELETE'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_delete_by_id(id):
    try : 
        with get_session() as db:
            user = db.query(User).filter_by(id=id).first()  
            user.is_active = False 
            user.deleted_at = datetime.utcnow()
            db.commit() 
    except Exception as e:
        return { "message" : f"error : {e}"}, 500
    
    return { "message" : "User deleted."}, 200


@system_admin_bp.route('/users/<int:id>/role',methods=['PATCH'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_user_change_role_by_id(id):
    try : 
        data = request.get_json()
        print(data)
        with get_session() as db:
            user = db.query(User).filter_by(id=id).first()   
            user.role = data['role']
            db.commit() 
    except Exception as e:
        return { "message" : f"error : {e}"}, 500
    
    return { "message" : "Status Changed."}, 200



@system_admin_bp.route('/universities', methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_get_universities():
    try:
        with get_session() as db:
            universities = db.query(University).all()
            result = [{
                "id": university.id,
                "name": university.name,
                "short_name": university.short_name,
                "logo_url": university.logo_url,
                "domain": university.domain,
                "address": university.address,
                "website": university.website,
                "banner": university.banner,
                "is_active": university.is_active
            } for university in universities]
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    return jsonify(result)
    pass
    
@system_admin_bp.route('/universities', methods=['POST'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_create_university():
    try:
        data = request.get_json()
        #print(data)
        name = data.get('name')
        domain = data.get('domain')
        banner_img_data = data.get('banner') #optional
        allowed_domains = data.get('allowed_domains') #optional
        is_active = data.get('is_active')

        bnner_img_file_url = None
        if banner_img_data:
            bnner_img_file_url = save_base64_image(banner_img_data)
            pass
        with get_session() as db:
            created_at = datetime.utcnow()
            new_university = University(
                name=name,
                domain=domain,
                banner=bnner_img_file_url,
                is_active=is_active,
                created_at=created_at
            )
            db.add(new_university)
            db.flush()
            if allowed_domains:
                for domain in allowed_domains:
                    created_at = created_at
                    university_domain = UniversityDomain(university_id=new_university.id,domain=domain['domain'],created_at=created_at)
                    db.add(university_domain)
            db.commit()

    except Exception as e:
        return { 'message' : f"Error : {e}"}, 500
    
    return { 'message' : "University created successfully"}, 200


@system_admin_bp.route('/universities/<int:id>', methods=['PATCH'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_update_universitiy_by_id(id):
    try:
        data = request.get_json()
        #{'name': 'Indian Institute of Technology Delhi', 'domain': 'iitd.ac.in', 'banner': '', 'allowed_domains': [], 'is_active': False}
        name = data.get('name')
        domain = data.get('domain')
        banner_img_data = data.get('banner') #optional
        allowed_domains = data.get('allowed_domains') #optional
        is_active = data.get('is_active')
        print(data)
        bnner_img_file_url = None
        if banner_img_data and banner_img_data.startswith("data:image/"):
            bnner_img_file_url = save_base64_image(banner_img_data)
            pass
        with get_session() as db:
            university = db.query(University).filter_by(id=id).first()
            if not university:
                return { 'message' : "University Not found."}, 404
            university.name = name
            university.domain = domain
            university.is_active = is_active
            university.updated_at = datetime.utcnow()
            if bnner_img_file_url:
                if university.banner:
                    delete_uploaded_file(university.banner)
                university.banner = bnner_img_file_url
            if allowed_domains:
                for domain in allowed_domains:
                    created_at = university.updated_at
                    university_domain = UniversityDomain(university_id=id,domain=domain['domain'],created_at=created_at)
                    db.add(university_domain)
            db.commit()
    except Exception as e:
        print(e)
        return { 'message' : f"Error : {e}"}, 500

    return { 'message' : "University updated successfully"}, 200



@system_admin_bp.route('/users/recent', methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_support_get_tickets():
    try : 
        with get_session() as db:
            recent_users = (db.query(User).outerjoin(User.department).outerjoin(User.university)
                            .order_by(User.created_at.desc())
                            .limit(5)
                            .all())   
            result = [
                {
                    "id" : user.id,
                    "full_name" : user.full_name,
                    "email" : user.email,
                    "role" : user.role,
                    "is_active" : user.is_active,
                    "created_at" : user.created_at,
                    "university_name" : user.university.name if user.university else None,
                    "department" : user.department.name if user.department else None,
                    "roll_number" : user.roll_number

                } for user in recent_users
            ]              
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    
    return jsonify(result)

            
@system_admin_bp.route('/support/recent', methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_support_get_recent_ticket_by_id():
    try : 
        with get_session() as db:
            recent_tkts = (db.query(SupportTicket)
                            .order_by(SupportTicket.created_at.desc())
                            .limit(5)
                            .all())   
            result = [
                {
                    "id": tkt.id,
                    "raised_by": tkt.raised_by,
                    "club_id": tkt.club_id,
                    "title": tkt.title,
                    "description": tkt.description,
                    "ticket_type": tkt.ticket_type,
                    "priority": tkt.priority,
                    "status": tkt.status,
                    "assigned_agent_id": tkt.assigned_agent_id,
                    "is_offensive": tkt.is_offensive,
                    "resolution_rating": tkt.resolution_rating,
                    "university_id": tkt.university_id,
                    "created_at": tkt.created_at 

                } for tkt in recent_tkts
            ]              
    except Exception as e:
        print(e)
        return { "message" : f"error : {e}"}, 500
    
    return jsonify(result), 200

