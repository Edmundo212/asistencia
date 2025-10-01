from flask import Blueprint, request, jsonify
from models.attendance import mark_attendance, get_all_attendance

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/attendance", methods=["POST"])
def add_attendance():
    data = request.json
    user_id = data.get("user_id")
    status = data.get("status", "Present")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    record_id = mark_attendance(user_id, status)

    if record_id:
        return jsonify({"message": "Asistencia registrada", "attendance_id": record_id}), 201
    else:
        return jsonify({"error": "Failed to record attendance"}), 500

@attendance_bp.route("/attendance", methods=["GET"])
def view_attendance():
    records = get_all_attendance()
    return jsonify(records), 200
