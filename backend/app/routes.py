#Purpose of Routes.py: Establish All Our Routes for Using Flask | These are Essentially How Users/Data Are  Moved Throughout Our Entire Application 




from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, send_from_directory, session
from .storage import create_task, get_all_tasks, update_task, delete_task, generate_schedule

api = Blueprint("api", __name__)
auth = Blueprint("auth", __name__)

TEST_USERNAME = "admin"
TEST_PASSWORD = "momentum123"

#Handles user Logins | Takes Data -- Takes Username and Password | Returns Error if No match with Our System
@auth.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if username != TEST_USERNAME or password != TEST_PASSWORD:
        return jsonify({"error": "Invalid credentials"}), 401
    #Creates Session
    session["user"] = username

    return jsonify({
        "message": "Login successful",
        "user": username
    }), 200

#This is what Actually Routes the User to Our Login Section( Then our Login Method will allow then to login)
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper

#THis Our Route for When Users Logout | 
@auth.route("/api/logout", methods=["POST"])
def logout():
    #Gets Rid of Our Users Sessions
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200


#authentication Route For Verify the User is Here(Flow: Sent to Login  --  Required to Login -- Verification  )
@auth.route("/api/me", methods=["GET"])
def me():
    user = session.get("user")

    if not user:
        return jsonify({
            "authenticated": False,
            "user": None
        }), 200

    return jsonify({
        "authenticated": True,
        "user": user
    }), 200


# =========================
# STATIC PAGES
# =========================

@api.route("/", methods=["GET"])
def index():
    return send_from_directory("../../frontend", "index.html")


#Route For Sending to DashBoard HTML
@api.route("/dashboard.html", methods=["GET"])
def dashboard_page():
    return send_from_directory("../../frontend", "dashboard.html")

#Route for our Tasks 
@api.route("/tasks.html", methods=["GET"])
def tasks_page():
    return send_from_directory("../../frontend", "tasks.html")

#Routes for our Schedule
@api.route("/schedule.html", methods=["GET"])
def schedule_page():
    return send_from_directory("../../frontend", "schedule.html")

#Routes for our Login | This is where the user has to go to actually login 
@api.route("/login.html", methods=["GET"])
def login_page():
    return send_from_directory("../../frontend", "login.html")


# =========================
# HEALTH CHECK
# =========================

@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# =========================
# TASK ROUTES
# =========================


#This the Route for Our Tasks
@api.route("/api/tasks", methods=["GET"])
@login_required
def list_tasks():
    #Logic for sorting our tasks when saved
    sort_by = request.args.get("sort")
    tasks = get_all_tasks(sort_by=sort_by)
    now = datetime.now()
    #OverDue Check on Our Current Saved assignemnts
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
        #This is the Data the USer Will See When Creating a Tasks
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
            "description": t["description"],
            "notes": t["notes"],
            "is_overdue": check_overdue(t["due_date"], t["status"])
        }
        for t in tasks
    ]

    return jsonify(response), 200



@api.route("/api/tasks", methods=["POST"])
@login_required
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
@login_required
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


@api.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def remove_task(task_id):
    deleted = delete_task(task_id)

    if not deleted:
        return jsonify({"error": "Task could not be deleted."}), 404

    return jsonify({"message": "Task deleted successfully."}), 200


# =========================
# SCHEDULE ROUTE
# =========================

@api.route("/api/schedule", methods=["POST"])
@login_required
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