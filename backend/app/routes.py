"""
========================================================
ROUTES.PY OVERVIEW — MOMENTUM APPLICATION | Disclaimer -- Ariticial Intelligence was used to ORGANIZE Our NOTES, FIX BUGS, and WORK WITH INDENTATION ISSUES
========================================================

Purpose:
This file defines the main Flask routes for the Momentum
application. It acts as the controller layer of the system,
connecting frontend requests to backend logic and returning
the appropriate responses.

High-Level Responsibility:
routes.py is responsible for:
1. Serving frontend HTML pages
2. Handling authentication routes
3. Handling task-related API requests
4. Handling schedule-generation API requests
5. Validating incoming request data before passing it to
   the backend storage / scheduling layer

--------------------------------------------------------
ARCHITECTURAL ROLE
--------------------------------------------------------

This file primarily serves as the Controller layer in the
project’s MVC-style structure:

- Model / Data Layer:
  database.py and storage.py
- View Layer:
  index.html, dashboard.html, tasks.html, schedule.html,
  login.html, plus frontend rendering in JavaScript
- Controller Layer:
  routes.py

routes.py does not directly implement most database logic
or scheduling logic itself. Instead, it:
- receives requests from the frontend
- validates and organizes input
- calls backend helper functions such as:
    create_task()
    get_all_tasks()
    update_task()
    delete_task()
    generate_schedule()
- returns structured JSON responses to the frontend

--------------------------------------------------------
MAIN FUNCTIONAL AREAS
--------------------------------------------------------

1. Authentication Routes
These routes manage login, logout, and session checking.

Examples:
- /api/login
- /api/logout
- /api/me

Purpose:
- verify user credentials
- create or remove session data
- protect other routes through login_required

2. Static Page Routes
These routes serve the application’s frontend HTML pages.

Examples:
- /
- /dashboard.html
- /tasks.html
- /schedule.html
- /login.html

Purpose:
- load the correct frontend page for the user
- connect Flask backend routing with the web interface

3. Task API Routes
These routes manage CRUD operations for tasks.

Examples:
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/<task_id>
- DELETE /api/tasks/<task_id>

Purpose:
- retrieve tasks from the database
- create new tasks
- update existing tasks
- delete tasks
- compute additional response fields such as overdue status

4. Schedule API Route
This route generates a schedule from saved tasks.

Example:
- POST /api/schedule

Purpose:
- accept schedule constraints such as number of days and
  max tasks per day
- call the scheduling engine
- return a structured schedule for frontend rendering

--------------------------------------------------------
VALIDATION RESPONSIBILITY
--------------------------------------------------------

routes.py is also responsible for validating request data
before sending it into the backend logic.

Examples of validation include:
- required fields such as title and due_date
- allowed values such as priority and effort level
- numeric checks such as duration_minutes > 0
- datetime string validation for fields like start_after

This prevents invalid user input from breaking database
operations or scheduling logic.

--------------------------------------------------------
SECURITY RESPONSIBILITY
--------------------------------------------------------

Protected API routes use the login_required decorator.

Purpose:
- ensure only authenticated users can access task and
  schedule functionality
- prevent unauthorized users from interacting with
  protected application data

--------------------------------------------------------
WHY THIS FILE IS IMPORTANT
--------------------------------------------------------

routes.py is the central communication layer of the app.
It coordinates:
- frontend pages
- user actions
- backend processing
- API responses

Without this file, the frontend would have no way to:
- request task data
- create or update tasks
- generate schedules
- authenticate users

In summary, routes.py is the backbone of request handling
in Momentum and ensures the application behaves as a
structured, secure, and interactive full-stack system.

========================================================
"""
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, send_from_directory, session
from .storage import create_task, get_all_tasks, update_task, delete_task, generate_schedule
from datetime import datetime

# Main blueprints
api = Blueprint("api", __name__)
auth = Blueprint("auth", __name__)

TEST_USERNAME = "admin"
TEST_PASSWORD = "momentum123"


# =========================
# AUTH ROUTES( Login, Login_Required, Logout, Verify the User ) -- All of this is what we uses for Our Login 
# =========================





@auth.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if username != TEST_USERNAME or password != TEST_PASSWORD:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = username

    return jsonify({
        "message": "Login successful",
        "user": username
    }), 200


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


@auth.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200


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
# STATIC PAGES/Entry Points into our Application 
# =========================


# -----------------------------------------------
# Helper: Validate Datetime String Format
# -----------------------------------------------
# Purpose:
# Ensures that a given string follows the expected datetime format
# ("YYYY-MM-DD HH:MM") before it is processed or stored.
#
# Why it matters:
# Prevents runtime errors during parsing, protects scheduling logic,
# and ensures only valid datetime values are used throughout the system.
#
# Returns:
# True if valid format, False otherwise
def is_valid_datetime_string(value):
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except (TypeError, ValueError):
        return False


# -----------------------------------------------
# Route: Landing Page
# -----------------------------------------------
# Purpose:
# Serves the main entry point of the application (index.html).
#
# Behavior:
# When a user visits the root URL ("/"), this route loads
# the frontend landing page.

@api.route("/", methods=["GET"])
def index():
    return send_from_directory("../../frontend", "index.html")


# -----------------------------------------------
# Route: Dashboard Page
# -----------------------------------------------
# Purpose:
# Serves the main dashboard interface where users can view
# high-level information and interact with the app.
#
# Behavior:
# Loads dashboard.html from the frontend directory.

@api.route("/dashboard.html", methods=["GET"])
def dashboard_page():
    return send_from_directory("../../frontend", "dashboard.html")

# -----------------------------------------------
# Route: Tasks Page
# -----------------------------------------------
# Purpose:
# Serves the tasks management interface where users can
# create, view, edit, and delete tasks.
#
# Behavior:
# Loads tasks.html from the frontend directory.


@api.route("/tasks.html", methods=["GET"])
def tasks_page():
    return send_from_directory("../../frontend", "tasks.html")

# -----------------------------------------------
# Route: Schedule Page
# -----------------------------------------------
# Purpose:
# Serves the schedule view where users can see their tasks
# organized into a generated schedule with time blocks.
#
# Behavior:
# Loads schedule.html from the frontend directory.

@api.route("/schedule.html", methods=["GET"])
def schedule_page():
    return send_from_directory("../../frontend", "schedule.html")

# -----------------------------------------------
# Route: Login Page
# -----------------------------------------------
# Purpose:
# Serves the authentication interface where users can log in
# to access the application.
#
# Behavior:
# Loads login.html from the frontend directory.

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
# TASK ROUTES(Ex: LIST, ADD, EDIT, DELETE)
# =========================









# -----------------------------------------------
# Route: Get All Tasks (With Optional Sorting)
# -----------------------------------------------
# Purpose:
# Retrieves all tasks from the database and returns them
# in a structured JSON format for the frontend.
#
# Features:
# - Supports optional sorting (by date or priority)
# - Calculates whether each task is overdue
# - Transforms raw database rows into API-friendly objects
#
# Security:
# - Protected by @login_required (user must be authenticated)
#
# Returns:
# JSON list of tasks with computed "is_overdue" field


@api.route("/api/tasks", methods=["GET"])
@login_required
def list_tasks():
    sort_by = request.args.get("sort")
    tasks = get_all_tasks(sort_by=sort_by)
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


# -----------------------------------------------
# Route: Create New Task
# -----------------------------------------------
# Purpose:
# Accepts task data from the frontend, validates inputs,
# and inserts a new task into the database.
#
# Features:
# - Extracts and sanitizes input fields from request body
# - Validates required fields (title, due_date, priority)
# - Enforces constraints (duration, effort level, priority)
# - Validates optional datetime fields (start_after)
# - Creates task using database layer
# - Returns newly created task in JSON format
#
# Security:
# - Protected by @login_required (user must be authenticated)
#
# Returns:
# 201 Created → Task successfully created
# 400 Bad Request → Validation error


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

# -----------------------------------------------
# Route: Delete Task
# -----------------------------------------------
# Purpose:
# Removes a task from the database based on its unique ID.
#
# Features:
# - Accepts task_id as a URL parameter
# - Calls storage layer to delete the task
# - Handles success and failure cases
#
# Security:
# - Protected by @login_required (user must be authenticated)
#
# Returns:
# 200 OK → Task successfully deleted
# 404 Not Found → Task does not exist or deletion failed

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




# -----------------------------------------------
# Route: Generate Schedule
# -----------------------------------------------
# Purpose:
# Generates a structured schedule based on existing tasks,
# using constraints such as number of days and max tasks per day.
#
# Features:
# - Accepts scheduling parameters from request body
# - Validates numeric inputs (days, max_tasks_per_day)
# - Calls scheduling logic to build optimized schedule
# - Handles empty schedule scenarios gracefully
#
# Security:
# - Protected by @login_required (user must be authenticated)
#
# Returns:
# 200 OK → Schedule generated (or no tasks available)
# 400 Bad Request → Invalid input values

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



bp = Blueprint("routes", __name__)


# -----------------------------------------------
# Route: Create Task (Alternate API Endpoint)
# -----------------------------------------------
# Purpose:
# Handles creation of a new task using data provided
# in the request body, then inserts it into the database.
#
# Features:
# - Extracts task data from JSON request
# - Supports extended fields (category, notes, link, etc.)
# - Validates required fields (title, due_date, priority)
# - Validates optional datetime fields (start_after)
# - Handles database insertion through storage layer
# - Returns created task or error response
#
# Returns:
# 200 OK → Task successfully created
# 400 Bad Request → Validation failure
# 500 Internal Server Error → Unexpected failure


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
