from flask import Blueprint, jsonify, request, send_from_directory
from .storage import create_task, get_all_tasks, update_task, delete_task, generate_schedule

api = Blueprint("api", __name__)

@api.route("/", methods=["GET"])
def index():
    return send_from_directory("../../frontend", "index.html")

@api.route("/dashboard.html", methods=["GET"])
def dashboard_page():
    return send_from_directory("../../frontend", "dashboard.html")

@api.route("/tasks.html", methods=["GET"])
def tasks_page():
    return send_from_directory("../../frontend", "tasks.html")

@api.route("/schedule.html", methods=["GET"])
def schedule_page():
    return send_from_directory("../../frontend", "schedule.html")

# Optional health check
@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# GET tasks (supports sorting)
@api.route("/api/tasks", methods=["GET"])
def list_tasks():
    sort_by = request.args.get("sort")
    tasks = get_all_tasks(sort_by=sort_by)

    response = [
        {
            "id": t["task_id"],
            "title": t["title"],
            "status": t["status"],
            "due_date": t["due_date"],
            "priority": t["priority"],
            "duration_minutes": t["duration_minutes"],
            "effort_level": t["effort_level"],
            "start_after": t["start_after"],
            "category": t["category"]
        }
        for t in tasks
    ]
    return jsonify(response), 200


# POST create task
@api.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    due_date = (data.get("due_date") or "").strip()
    priority = (data.get("priority") or "").strip()

    duration_minutes = data.get("duration_minutes", 60)
    effort_level = (data.get("effort_level") or "Medium").strip()
    start_after = (data.get("start_after") or "").strip() or None
    category = (data.get("category") or "General").strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400
    if not due_date:
        return jsonify({"error": "Due date is required."}), 400
    if priority not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Priority must be Low, Medium, or High."}), 400

    try:
        duration_minutes = int(duration_minutes)
        if duration_minutes <= 0:
            return jsonify({"error": "Duration must be greater than 0."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Duration must be a valid number."}), 400

    if effort_level not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Effort level must be Low, Medium, or High."}), 400

    task = create_task(
        title,
        due_date,
        priority,
        duration_minutes,
        effort_level,
        start_after,
        category
    )

    return jsonify({
        "id": task["task_id"],
        "title": task["title"],
        "status": task["status"],
        "due_date": task["due_date"],
        "priority": task["priority"],
        "duration_minutes": task["duration_minutes"],
        "effort_level": task["effort_level"],
        "start_after": task["start_after"],
        "category": task["category"]
    }), 201

# PUT edit task
@api.route("/api/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    due_date = (data.get("due_date") or "").strip()
    priority = (data.get("priority") or "").strip()
    status = (data.get("status") or "").strip()

    duration_minutes = data.get("duration_minutes", 60)
    effort_level = (data.get("effort_level") or "Medium").strip()
    start_after = (data.get("start_after") or "").strip() or None
    category = (data.get("category") or "General").strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400
    if not due_date:
        return jsonify({"error": "Due date is required."}), 400
    if priority not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Priority must be Low, Medium, or High."}), 400
    if status not in {"Pending", "Not Started", "In Progress", "Completed"}:
        return jsonify({"error": "Status must be Pending, Not Started, In Progress, or Completed."}), 400

    try:
        duration_minutes = int(duration_minutes)
        if duration_minutes <= 0:
            return jsonify({"error": "Duration must be greater than 0."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Duration must be a valid number."}), 400

    if effort_level not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Effort level must be Low, Medium, or High."}), 400

    updated = update_task(
        task_id,
        title,
        due_date,
        priority,
        status,
        duration_minutes,
        effort_level,
        start_after,
        category
    )

    if not updated:
        return jsonify({"error": "Task not found."}), 404

    return jsonify({
        "message": "Task updated successfully.",
        "task": {
            "id": updated["task_id"],
            "title": updated["title"],
            "status": updated["status"],
            "due_date": updated["due_date"],
            "priority": updated["priority"],
            "duration_minutes": updated["duration_minutes"],
            "effort_level": updated["effort_level"],
            "start_after": updated["start_after"],
            "category": updated["category"]
        }
    }), 200

# DELETE task
@api.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    deleted = delete_task(task_id)

    if not deleted:
        return jsonify({"error": "Task could not be deleted."}), 404

    return jsonify({"message": "Task deleted successfully."}), 200


# POST generate schedule
@api.route("/api/schedule", methods=["POST"])
def build_schedule():
    data = request.get_json(silent=True) or {}

    try:
        days = int(data.get("days", 7))
    except (TypeError, ValueError):
        return jsonify({"error": "Days must be a valid number."}), 400

    try:
        max_tasks_per_day = int(data.get("max_tasks_per_day", 4))
        if max_tasks_per_day <= 0:
            return jsonify({"error": "Max tasks per day must be greater than 0."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Max tasks per day must be a valid number."}), 400

    schedule = generate_schedule(days=days, max_tasks_per_day=max_tasks_per_day)

    if not schedule:
        return jsonify({
            "message": "No tasks available to schedule.",
            "schedule": {}
        }), 200

    return jsonify({
        "message": "Schedule generated successfully.",
        "schedule": schedule
    }), 200

