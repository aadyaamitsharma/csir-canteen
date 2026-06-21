"""
seed_db.py — Run this once to populate the database with sample data.
Usage: python seed_db.py
"""
from app import create_app, db
from app.models import User, Department, IndentRequest, ApprovalLog, Rating
from datetime import date, time, datetime, timedelta
import random

app = create_app()

def seed():
    with app.app_context():
        print("Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()

        # ── DEPARTMENTS ──────────────────────────────────────────────
        dept_data = [
            ("Traffic Engineering & Safety", "TES"),
            ("Road Materials & Technology", "RMT"),
            ("Bridge Engineering", "BE"),
            ("Geotechnical Engineering", "GTE"),
            ("Highway Planning & Administration", "HPA"),
            ("Computer & IT Division", "CIT"),
        ]
        depts = []
        for name, code in dept_data:
            d = Department(name=name, code=code)
            db.session.add(d)
            depts.append(d)
        db.session.commit()
        print(f"✓ {len(depts)} departments created")

        # ── USERS ────────────────────────────────────────────────────
        users_data = [
            ("Admin User",      "admin@csir.in",     "EMP001", "admin",    "System Administrator", None),
            ("Dr. R.K. Sharma", "hod@csir.in",       "EMP002", "hod",      "Head of Department",   0),
            ("Dr. Priya Mehta", "hod2@csir.in",      "EMP007", "hod",      "Head of Department",   1),
            ("Mr. A.K. Singh",  "chairman@csir.in",  "EMP003", "chairman", "Chairman GH & Canteen",None),
            ("Mrs. S. Gupta",   "manager@csir.in",   "EMP004", "manager",  "Manager GH & Canteen", None),
            ("Rahul Kumar",     "indentor@csir.in",  "EMP005", "indentor", "Scientist",            0),
            ("Anita Verma",     "anita@csir.in",     "EMP006", "indentor", "Junior Scientist",     1),
            ("Vikram Nair",     "vikram@csir.in",    "EMP008", "indentor", "Research Associate",   2),
        ]
        users = {}
        for name, email, empid, role, desig, dept_idx in users_data:
            u = User(
                name=name, email=email, employee_id=empid,
                role=role, designation=desig,
                department_id=depts[dept_idx].id if dept_idx is not None else None,
                phone=f"98{random.randint(10000000,99999999)}"
            )
            u.set_password("csir@1234")
            db.session.add(u)
            users[email] = u
        db.session.commit()
        print(f"✓ {len(users)} users created")

        indentor1 = users["indentor@csir.in"]
        indentor2 = users["anita@csir.in"]
        indentor3 = users["vikram@csir.in"]
        hod1 = users["hod@csir.in"]
        chairman = users["chairman@csir.in"]
        manager = users["manager@csir.in"]

        # ── INDENT REQUESTS ──────────────────────────────────────────
        # 1. Completed request with rating
        r1 = IndentRequest(
            indent_number="CSIR-2024-10001",
            indentor_id=indentor1.id,
            department_id=depts[0].id,
            scheme_no="SCH/2024/001",
            event_type="meeting",
            event_description="Monthly Review Meeting",
            venue="Conference Hall A",
            event_date=date.today() - timedelta(days=10),
            event_time=time(10, 0),
            duration="2 hours",
            number_of_persons=15,
            special_instructions="Please arrange vegetarian snacks only.",
            service_type_1=True, service_quantity_1=15, service_time_1="10:00",
            service_type_4="working", service_quantity_4=15, service_time_4="13:00",
            status="completed"
        )
        db.session.add(r1)
        db.session.flush()
        db.session.add(ApprovalLog(indent_id=r1.id, approver_id=hod1.id, role="hod", action="approved", remarks="Approved for monthly review.", timestamp=datetime.utcnow()-timedelta(days=9)))
        db.session.add(ApprovalLog(indent_id=r1.id, approver_id=chairman.id, role="chairman", action="approved", remarks="Sanctioned.", timestamp=datetime.utcnow()-timedelta(days=8)))
        db.session.add(ApprovalLog(indent_id=r1.id, approver_id=manager.id, role="manager", action="completed", remarks="Service delivered successfully.", timestamp=datetime.utcnow()-timedelta(days=7)))
        db.session.add(Rating(indent_id=r1.id, rater_id=indentor1.id, food_quality=4, service_quality=5, timeliness=4, overall=4, feedback="Great service! Food was excellent."))

        # 2. In Progress
        r2 = IndentRequest(
            indent_number="CSIR-2024-10002",
            indentor_id=indentor2.id,
            department_id=depts[1].id,
            event_type="seminar",
            event_description="Road Safety Seminar",
            venue="Seminar Hall",
            event_date=date.today() + timedelta(days=2),
            event_time=time(9, 30),
            duration="Full Day",
            number_of_persons=40,
            service_type_2=True, service_quantity_2=40, service_time_2="09:30",
            service_type_3=True, service_quantity_3=40, service_time_3="12:00",
            service_type_4="special", service_quantity_4=40, service_time_4="13:30",
            status="in_progress"
        )
        db.session.add(r2)
        db.session.flush()
        db.session.add(ApprovalLog(indent_id=r2.id, approver_id=hod1.id, role="hod", action="approved", remarks="Approved for seminar.", timestamp=datetime.utcnow()-timedelta(days=3)))
        db.session.add(ApprovalLog(indent_id=r2.id, approver_id=chairman.id, role="chairman", action="approved", remarks="Sanctioned.", timestamp=datetime.utcnow()-timedelta(days=2)))
        db.session.add(ApprovalLog(indent_id=r2.id, approver_id=manager.id, role="manager", action="in_progress", remarks="Preparations underway.", timestamp=datetime.utcnow()-timedelta(days=1)))

        # 3. Pending HOD
        r3 = IndentRequest(
            indent_number="CSIR-2024-10003",
            indentor_id=indentor3.id,
            department_id=depts[2].id,
            event_type="training",
            event_description="New Joinees Orientation",
            venue="Training Room 1",
            event_date=date.today() + timedelta(days=5),
            event_time=time(11, 0),
            duration="3 hours",
            number_of_persons=20,
            service_type_1=True, service_quantity_1=20, service_time_1="11:00",
            service_type_4="regular", service_quantity_4=20, service_time_4="13:00",
            status="pending_hod"
        )
        db.session.add(r3)

        # 4. Chairman Approved (awaiting manager)
        r4 = IndentRequest(
            indent_number="CSIR-2024-10004",
            indentor_id=indentor1.id,
            department_id=depts[0].id,
            event_type="conference",
            event_description="National Road Infrastructure Conference",
            venue="Main Auditorium",
            event_date=date.today() + timedelta(days=7),
            event_time=time(9, 0),
            duration="2 days",
            number_of_persons=80,
            special_instructions="VIP arrangements required.",
            service_type_2=True, service_quantity_2=80, service_time_2="09:00",
            service_type_4="executive", service_quantity_4=80, service_time_4="13:00",
            status="chairman_approved"
        )
        db.session.add(r4)
        db.session.flush()
        db.session.add(ApprovalLog(indent_id=r4.id, approver_id=hod1.id, role="hod", action="approved", remarks="Important national conference.", timestamp=datetime.utcnow()-timedelta(days=2)))
        db.session.add(ApprovalLog(indent_id=r4.id, approver_id=chairman.id, role="chairman", action="approved", remarks="Sanctioned. Ensure VIP service.", timestamp=datetime.utcnow()-timedelta(days=1)))

        # 5. HOD Rejected
        r5 = IndentRequest(
            indent_number="CSIR-2024-10005",
            indentor_id=indentor2.id,
            department_id=depts[1].id,
            event_type="meeting",
            event_description="Informal team gathering",
            venue="Open Lawn",
            event_date=date.today() - timedelta(days=5),
            event_time=time(17, 0),
            duration="1 hour",
            number_of_persons=10,
            service_type_3=True, service_quantity_3=10,
            status="hod_rejected"
        )
        db.session.add(r5)
        db.session.flush()
        db.session.add(ApprovalLog(indent_id=r5.id, approver_id=hod1.id, role="hod", action="rejected", remarks="Informal gatherings not covered under canteen indent policy.", timestamp=datetime.utcnow()-timedelta(days=4)))

        # 6. Another completed with rating
        r6 = IndentRequest(
            indent_number="CSIR-2024-10006",
            indentor_id=indentor3.id,
            department_id=depts[3].id,
            event_type="meeting",
            event_description="Project Review",
            venue="Board Room",
            event_date=date.today() - timedelta(days=20),
            event_time=time(14, 0),
            number_of_persons=8,
            service_type_1=True, service_quantity_1=8, service_time_1="14:00",
            status="completed"
        )
        db.session.add(r6)
        db.session.flush()
        db.session.add(ApprovalLog(indent_id=r6.id, approver_id=hod1.id, role="hod", action="approved", timestamp=datetime.utcnow()-timedelta(days=19)))
        db.session.add(ApprovalLog(indent_id=r6.id, approver_id=chairman.id, role="chairman", action="approved", timestamp=datetime.utcnow()-timedelta(days=18)))
        db.session.add(ApprovalLog(indent_id=r6.id, approver_id=manager.id, role="manager", action="completed", timestamp=datetime.utcnow()-timedelta(days=17)))
        db.session.add(Rating(indent_id=r6.id, rater_id=indentor3.id, food_quality=3, service_quality=4, timeliness=5, overall=4, feedback="On time delivery. Good."))

        db.session.commit()
        print("✓ 6 indent requests with approval logs and ratings created")

        print("\n" + "="*50)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)
        print("\nLogin credentials (all passwords: csir@1234):")
        print(f"  Admin    : admin@csir.in")
        print(f"  HOD      : hod@csir.in")
        print(f"  Chairman : chairman@csir.in")
        print(f"  Manager  : manager@csir.in")
        print(f"  Indentor : indentor@csir.in")
        print(f"  Indentor : anita@csir.in")
        print(f"  Indentor : vikram@csir.in")
        print("="*50)

if __name__ == '__main__':
    seed()
