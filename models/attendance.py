from datetime import datetime
from database.db import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('known_faces.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Present")

    def __repr__(self):
        return f"<Attendance {self.id} - User {self.user_id} - {self.status} at {self.timestamp}>"

def mark_attendance(user_id, status="Present"):
    record = Attendance(user_id=user_id, status=status)
    db.session.add(record)
    db.session.commit()
    return record.id

def get_all_attendance():
    from sqlalchemy import text
    query = text("""
        SELECT a.id, a.timestamp, a.status, u.nombre, u.apellido, u.dni
        FROM attendance a
        JOIN known_faces u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
    """)
    result = db.session.execute(query).fetchall()
    records = []
    for row in result:
        records.append({
            "id": row[0],
            "timestamp": row[1],
            "status": row[2],
            "nombre": row[3],
            "apellido": row[4],
            "dni": row[5]
        })
    return records
