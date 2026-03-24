from flask import Blueprint, jsonify, request, send_from_directory
from .storage import create_task, get_all_tasks, update_task, delete_task, generate_schedule
from datetime import datetime

api = Blueprint("api", __name__)

def is_valid_datetime_string(value):
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except (TypeError, ValueError):
        return False

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

@api.route("/api/tasks", methods=["GET"])
def list_tasks():
    sort_by = request.args.get("sort")
    tasks = get_all_tasks(sort_by=sort_by)

    from datetime import datetime
    now = datetime.now()

    def check_overdue(due_date, status):
        if status == "Completed" or not due_date:
            return False
        normalized = due_date.strip().replace(" ", "T")
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            except ValueError:
                return False
        return dt < now

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
            "category": t["category"],
            "is_overdue": check_overdue(t["due_date"], t["status"]),
            "description": t["description"],
            "notes": t["notes"]
        }
        for t in tasks
    ]
    return jsonify(response), 200

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
    description = (data.get("description") or "").strip()
    notes = (data.get("notes") or "").strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400
    if not due_date:
        return jsonify({"error": "Due date is required."}), 400
    if priority not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Priority must be Low, Medium, or High."}), 400
    if start_after and not is_valid_datetime_string(start_after):
        return jsonify({"error": "Invalid earliest start date format. Use YYYY-MM-DD HH:MM"}), 400

    try:
        duration_minutes = int(duration_minutes)
        if duration_minutes <= 0:
            return jsonify({"error": "Duration must be greater than 0."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Duration must be a valid number."}), 400

    if effort_level not in {"Low", "Medium", "High"}:
        return jsonify({"error": "Effort level must be Low, Medium, or High."}), 400

    task = create_task(
        title=title,
        due_date=due_date,
        priority=priority,
        duration_minutes=duration_minutes,
        effort_level=effort_level,
        start_after=start_after,
        category=category,
        description=description,
        notes=notes
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
        "category": task["category"],
        "description": task["description"],
        "notes": task["notes"]
    }), 201



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
    description = (data.get("description") or "").strip()
    notes = (data.get("notes") or "").strip()

    if start_after and not is_valid_datetime_string(start_after):
        return jsonify({"error": "Invalid earliest start date format. Use YYYY-MM-DD HH:MM"}), 400
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
        task_id=task_id,
        title=title,
        due_date=due_date,
        priority=priority,
        status=status,
        duration_minutes=duration_minutes,
        effort_level=effort_level,
        start_after=start_after,
        category=category,
        description=description,
        notes=notes
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
            "category": updated["category"],
            "description": updated["description"],
            "notes": updated["notes"]
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



bp = Blueprint("routes", __name__)


@bp.route("/api/tasks", methods=["POST"])
def api_create_task():
    data = request.get_json() or {}

    title = data.get("title")
    due_date = data.get("due_date")
    priority = data.get("priority")
    duration_minutes = data.get("duration_minutes", 60)
    effort_level = data.get("effort_level", "Medium")
    start_after = data.get("start_after")
    category = data.get("category", "General")
    description = data.get("description", "")
    notes = data.get("notes", "")
    link = data.get("link", "")

    if start_after and not is_valid_datetime_string(start_after):
        return jsonify({"error": "Invalid earliest start date format. Use YYYY-MM-DD HH:MM"}), 400

    if not title or not due_date or not priority:
        return jsonify({"error": "Title, due date, and priority are required."}), 400

    try:
        task = create_task(
            title=title,
            due_date=due_date,
            priority=priority,
            duration_minutes=duration_minutes,
            effort_level=effort_level,
            start_after=start_after,
            category=category,
            description=description,
            notes=notes,
            link=link
        )
        return jsonify(task), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    data = request.get_json() or {}

    title = data.get("title")
    due_date = data.get("due_date")
    priority = data.get("priority")
    status = data.get("status")
    duration_minutes = data.get("duration_minutes", 60)
    effort_level = data.get("effort_level", "Medium")
    start_after = data.get("start_after")
    category = data.get("category", "General")
    description = data.get("description", "")
    notes = data.get("notes", "")
    link = data.get("link", "")

    if not title or not due_date or not priority or not status:
        return jsonify({"error": "Missing required fields."}), 400

    try:
        task = update_task(
            task_id=task_id,
            title=title,
            due_date=due_date,
            priority=priority,
            status=status,
            duration_minutes=duration_minutes,
            effort_level=effort_level,
            start_after=start_after,
            category=category,
            description=description,
            notes=notes,
            link=link
        )

        if not task:
            return jsonify({"error": "Task not found."}), 404

        return jsonify(task), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
