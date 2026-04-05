"""
========================================================
USER STORY → FUNCTION MAPPING (Momentum Backend) -- Ariticial Intelligence was used to ORGANIZE Our NOTES, FIX BUGS, and WORK WITH INDENTATION ISSUES
========================================================

-------------------------------
TASK MANAGEMENT
-------------------------------

User Story: Create Task
- Inserts a new task into the database with default status
- Returns the created task record
→ create_task()

User Story: View Tasks
- Retrieves all stored tasks from the database
- Supports optional sorting
→ get_all_tasks()

User Story: Edit Task
- Updates an existing task in the database
- Returns the updated task record
→ update_task()

User Story: Delete Task
- Removes a task from the database
- Returns whether deletion succeeded
→ delete_task()


-------------------------------
SCHEDULE GENERATION
-------------------------------

User Story: Generate Schedule
- Builds a schedule using due date, priority, effort level,
  duration, category, and start constraints
→ generate_schedule()

User Story: Duration-Based Scheduling
- Assigns start/end times based on task duration
→ assign_times_for_day()
→ format_time_range()

User Story: Effort-Level Scheduling
- Prioritizes higher-effort tasks when due date and priority
  are otherwise equal
→ generate_schedule()

User Story: Priority-Based Scheduling
- Orders tasks using due date first, then priority
→ generate_schedule()

User Story: Start Constraint Scheduling
- Prevents a task from being scheduled before its allowed
  start date/time
→ parse_task_datetime()
→ generate_schedule()

User Story: Max Tasks Per Day
- Limits how many tasks can be placed on a single day
→ generate_schedule()

User Story: Multi-Day Task Distribution
- Spreads tasks across the selected schedule range
→ generate_schedule()


-------------------------------
SCHEDULE ORGANIZATION
-------------------------------

User Story: Category Balancing
- Reorders tasks within a day to avoid clustering the same
  category back-to-back when possible
→ balance_categories()

User Story: Time Range Formatting
- Converts calculated start/end datetimes into readable
  strings for the frontend calendar
→ format_time_range()

User Story: Datetime Parsing
- Converts stored task datetime strings into Python datetime
  objects for scheduling comparisons
→ parse_task_datetime()


-------------------------------
ARCHITECTURE NOTE
-------------------------------

Database Layer
- create_task()
- get_all_tasks()
- update_task()
- delete_task()

Scheduling Logic Layer
- generate_schedule()
- balance_categories()
- assign_times_for_day()

Utility / Helper Layer
- parse_task_datetime()
- format_time_range()

========================================================
"""


"""
========================================================
USER STORY → FUNCTION MAPPING (Momentum Backend)
========================================================

-------------------------------
TASK MANAGEMENT
-------------------------------

User Story: Create Task
- Inserts a new task into the database with default status
- Supports description and notes fields
- Returns the created task record
→ create_task()

User Story: View Tasks
- Retrieves all stored tasks from the database
- Supports optional sorting
→ get_all_tasks()

User Story: Edit Task
- Updates an existing task in the database
- Supports updating description and notes
- Returns the updated task record
→ update_task()

User Story: Delete Task
- Removes a task from the database
- Returns whether deletion succeeded
→ delete_task()


-------------------------------
SCHEDULE GENERATION
-------------------------------

User Story: Generate Schedule
- Builds a schedule using due date, priority, effort level,
  duration, category, and start constraints
→ generate_schedule()

User Story: Duration-Based Scheduling
- Assigns start/end times based on task duration
→ assign_times_for_day()
→ format_time_range()

User Story: Effort-Level Scheduling
- Prioritizes higher-effort tasks when due date and priority
  are otherwise equal
→ generate_schedule()

User Story: Priority-Based Scheduling
- Orders tasks using due date first, then priority
→ generate_schedule()

User Story: Start Constraint Scheduling
- Prevents a task from being scheduled before its allowed
  start date/time
→ parse_task_datetime()
→ generate_schedule()

User Story: Max Tasks Per Day
- Limits how many tasks can be placed on a single day
→ generate_schedule()

User Story: Multi-Day Task Distribution
- Spreads tasks across the selected schedule range
→ generate_schedule()


-------------------------------
SCHEDULE ORGANIZATION
-------------------------------

User Story: Category Balancing
- Reorders tasks within a day to avoid clustering the same
  category back-to-back when possible
→ balance_categories()

User Story: Time Range Formatting
- Converts calculated start/end datetimes into readable
  strings for the frontend calendar
→ format_time_range()

User Story: Datetime Parsing
- Converts stored task datetime strings into Python datetime
  objects for scheduling comparisons
→ parse_task_datetime()


-------------------------------
ARCHITECTURE NOTE
-------------------------------

Database Layer
- create_task()
- get_all_tasks()
- update_task()
- delete_task()

Scheduling Logic Layer
- generate_schedule()
- balance_categories()
- assign_times_for_day()

Utility / Helper Layer
- parse_task_datetime()
- format_time_range()

========================================================
"""

"""
========================================================
USER STORY → FUNCTION MAPPING (Momentum Backend)
========================================================

-------------------------------
TASK MANAGEMENT
-------------------------------

User Story: Create Task
- Inserts a new task into the database with default status
- Supports description and notes fields
- Returns the created task record
→ create_task()

User Story: View Tasks
- Retrieves all stored tasks from the database
- Supports optional sorting
→ get_all_tasks()

User Story: Edit Task
- Updates an existing task in the database
- Supports updating description and notes
- Returns the updated task record
→ update_task()

User Story: Delete Task
- Removes a task from the database
- Returns whether deletion succeeded
→ delete_task()


-------------------------------
SCHEDULE GENERATION
-------------------------------

User Story: Generate Schedule
- Builds a schedule using due date, priority, effort level,
  duration, category, and start constraints
→ generate_schedule()

User Story: Duration-Based Scheduling
- Assigns start/end times based on task duration
→ assign_times_for_day()
→ format_time_range()

User Story: Effort-Level Scheduling
- Prioritizes higher-effort tasks when due date and priority
  are otherwise equal
→ generate_schedule()

User Story: Priority-Based Scheduling
- Orders tasks using due date first, then priority
→ generate_schedule()

User Story: Start Constraint Scheduling
- Prevents a task from being scheduled before its allowed
  start date/time
→ parse_task_datetime()
→ generate_schedule()

User Story: Max Tasks Per Day
- Limits how many tasks can be placed on a single day
→ generate_schedule()

User Story: Multi-Day Task Distribution
- Spreads tasks across the selected schedule range
→ generate_schedule()


-------------------------------
SCHEDULE ORGANIZATION
-------------------------------

User Story: Category Balancing
- Reorders tasks within a day to avoid clustering the same
  category back-to-back when possible
→ balance_categories()

User Story: Time Range Formatting
- Converts calculated start/end datetimes into readable
  strings for the frontend calendar
→ format_time_range()

User Story: Datetime Parsing
- Converts stored task datetime strings into Python datetime
  objects for scheduling comparisons
→ parse_task_datetime()


-------------------------------
ARCHITECTURE NOTE
-------------------------------

Database Layer
- create_task()
- get_all_tasks()
- update_task()
- delete_task()

Scheduling Logic Layer
- generate_schedule()
- balance_categories()
- assign_times_for_day()

Utility / Helper Layer
- parse_task_datetime()
- format_time_range()

========================================================
"""

from datetime import datetime, timedelta, time
from .database import get_connection


def create_task(
    title,
    due_date,
    priority,
    duration_minutes=60,
    effort_level="Medium",
    start_after=None,
    category="General",
    description="",
    notes=""
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            title,
            due_date,
            priority,
            status,
            duration_minutes,
            effort_level,
            start_after,
            category,
            description,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        due_date,
        priority,
        "Pending",
        duration_minutes,
        effort_level,
        start_after,
        category,
        description,
        notes
    ))

    conn.commit()
    task_id = cursor.lastrowid

    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    conn.close()
    return dict(task)


def get_all_tasks(sort_by=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks"

    if sort_by == "date":
        query += " ORDER BY due_date ASC"
    elif sort_by == "priority":
        query += """
        ORDER BY
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
            ELSE 99
        END
        """

    cursor.execute(query)
    tasks = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return tasks


def update_task(
    task_id,
    title,
    due_date,
    priority,
    status,
    duration_minutes,
    effort_level,
    start_after,
    category,
    description="",
    notes=""
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET
            title = ?,
            due_date = ?,
            priority = ?,
            status = ?,
            duration_minutes = ?,
            effort_level = ?,
            start_after = ?,
            category = ?,
            description = ?,
            notes = ?
        WHERE task_id = ?
    """, (
        title,
        due_date,
        priority,
        status,
        duration_minutes,
        effort_level,
        start_after,
        category,
        description,
        notes,
        task_id
    ))

    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    conn.close()
    return dict(task) if task else None

'''

USer Story #4: Delete Task -- Gets Rid of Any Task Which We Don't Want In Our Database(For the User Any Tasks they don't want on their calendar)

'''


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    #Query for executuing Deletion 
    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()
    return deleted


'''
User Story #12: Schedule Time Display 
Purpose: Display Our Start and End Time in an Organized Format

'''

#This is a Helper Method for Formatting our Dates 
def format_time_range(start_dt, duration_minutes):
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return (
        start_dt.strftime("%-I:%M %p"),
        end_dt.strftime("%-I:%M %p")
    )

'''

User Story #13: Category Distribution 
Purpose: Based on the Category of Our Tasks We Will Have Tasks Back to back unless we have to 

'''


def balance_categories(tasks):
    remaining = tasks[:]
    balanced = []
   # Go Through List
    while remaining:
        #If Nothing Has Been Taken Yet, Take Out First Element
        if not balanced:
            balanced.append(remaining.pop(0))
            continue
        
        #Check Category last Popped 
        last_category = balanced[-1]["category"]
        

        #Swap if similir, it not keep going
        swap_index = None
        for i, task in enumerate(remaining):
            if task["category"] != last_category:
                swap_index = i
                break

        if swap_index is not None:
            balanced.append(remaining.pop(swap_index))
        else:
            balanced.append(remaining.pop(0))

    return balanced


def balance_effort_levels(tasks):
    remaining = tasks[:]
    balanced = []

    while remaining:
        if not balanced:
            balanced.append(remaining.pop(0))
            continue

        last_effort = balanced[-1]["effort_level"]

        swap_index = None
        for i, task in enumerate(remaining):
            if last_effort == "High":
                if task["effort_level"] != "High":
                    swap_index = i
                    break
            else:
                swap_index = 0
                break

        if swap_index is not None:
            balanced.append(remaining.pop(swap_index))
        else:
            balanced.append(remaining.pop(0))

    return balanced

'''
User Story #12: Schedule Display
Purpose: Works in Cohesion With  format_time_range -- this will turn string into a datetme format -- then format_time_rnage will format into start-end time

'''
def parse_task_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return None


def assign_times_for_day(tasks, day_date):
    current_start = datetime.combine(day_date, time(9, 0))
    scheduled_tasks = []
    unscheduled_tasks = []

    for task in tasks:
        duration_minutes = int(task["duration_minutes"]) if task.get("duration_minutes") else 60

        start_after_dt = parse_task_datetime(task.get("start_after"))
        due_dt = parse_task_datetime(task.get("due_date"))

        if start_after_dt and start_after_dt.date() == day_date:
            if current_start < start_after_dt:
                current_start = start_after_dt

        proposed_end = current_start + timedelta(minutes=duration_minutes)

        if due_dt and due_dt.date() == day_date and proposed_end > due_dt:
            unscheduled_tasks.append({
                **task,
                "reason": "Task could not fit before its due time on the assigned day."
            })
            continue

        start_time_str, end_time_str = format_time_range(current_start, duration_minutes)

        task["scheduled_start"] = start_time_str
        task["scheduled_end"] = end_time_str

        scheduled_tasks.append(task)
        current_start = proposed_end

    return scheduled_tasks, unscheduled_tasks


'''
User Story #6: Generate Schedule

'''

def generate_schedule(days=7, max_tasks_per_day=4):
    tasks = get_all_tasks(sort_by="date")

    # Ignore completed tasks
    tasks = [t for t in tasks if t["status"] != "Completed"]

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    effort_order = {"High": 0, "Medium": 1, "Low": 2}

    today = datetime.now().date()
    end_date = today + timedelta(days=days - 1)

    filtered_tasks = []
    unscheduled_tasks = []
    capacity_conflicts = []

    for task in tasks:
        task_due_dt = parse_task_datetime(task.get("due_date"))
        if not task_due_dt:
            continue

        task_due = task_due_dt.date()

        start_after_dt = parse_task_datetime(task.get("start_after"))
        start_after_date = start_after_dt.date() if start_after_dt else today

        if today <= task_due <= end_date and start_after_date <= end_date:
            filtered_tasks.append(task)

    # Sort by due date, priority, then effort
    filtered_tasks.sort(
        key=lambda t: (
            parse_task_datetime(t["due_date"]),
            priority_order.get(t["priority"], 99),
            effort_order.get(t["effort_level"], 99)
        )
    )

    grouped_schedule = {}
    tasks_per_day = {}

    for task in filtered_tasks:
        due_dt = parse_task_datetime(task.get("due_date"))
        due_day = due_dt.date() if due_dt else end_date

        start_after_dt = parse_task_datetime(task.get("start_after"))
        earliest_day = max(today, start_after_dt.date()) if start_after_dt else today
        latest_day = min(due_day, end_date)

        assigned_day = None
        current_day = earliest_day

        while current_day <= latest_day:
            day_key = current_day.strftime("%Y-%m-%d")
            count = tasks_per_day.get(day_key, 0)

            if count < max_tasks_per_day:
                assigned_day = current_day
                break

            current_day += timedelta(days=1)

        # NEW: track capacity conflict instead of silently skipping
        if not assigned_day:
            unscheduled_tasks.append({
                "id": task["task_id"],
                "title": task["title"],
                "status": task["status"],
                "due_date": task["due_date"],
                "priority": task["priority"],
                "duration_minutes": int(task["duration_minutes"]) if task.get("duration_minutes") else 60,
                "effort_level": task["effort_level"],
                "start_after": task["start_after"],
                "category": task["category"],
                "description": task.get("description", ""),
                "notes": task.get("notes", ""),
                "reason": "No available slot within the selected schedule range and max tasks per day limit."
            })
            continue

        day_key = assigned_day.strftime("%Y-%m-%d")

        if day_key not in grouped_schedule:
            grouped_schedule[day_key] = []

        duration_minutes = int(task["duration_minutes"]) if task.get("duration_minutes") else 60

        grouped_schedule[day_key].append({
            "id": task["task_id"],
            "title": task["title"],
            "status": task["status"],
            "due_date": task["due_date"],
            "priority": task["priority"],
            "duration_minutes": duration_minutes,
            "effort_level": task["effort_level"],
            "start_after": task["start_after"],
            "category": task["category"],
            "description": task.get("description", ""),
            "notes": task.get("notes", "")
        })

        tasks_per_day[day_key] = tasks_per_day.get(day_key, 0) + 1

    # Final pass:
    # 1. balance categories within each day
    # 2. balance effort levels
    # 3. assign time ranges
    for day_key, day_tasks in grouped_schedule.items():
        balanced_tasks = balance_categories(day_tasks)
        balanced_tasks = balance_effort_levels(balanced_tasks)
        day_date = datetime.strptime(day_key, "%Y-%m-%d").date()

        scheduled_tasks_for_day, day_unscheduled = assign_times_for_day(balanced_tasks, day_date)
        grouped_schedule[day_key] = scheduled_tasks_for_day
        unscheduled_tasks.extend(day_unscheduled)
    # NEW: summarize capacity conflicts
    # NEW: summarize conflicts
    if unscheduled_tasks:
        capacity_conflicts.append({
        "type": "Scheduling Conflict",
        "message": f"{len(unscheduled_tasks)} task(s) could not be scheduled due to time constraints, start_after limits, or daily capacity limits.",
        "count": len(unscheduled_tasks)
     })

    return {   
    "schedule": grouped_schedule,
    "capacity_conflicts": capacity_conflicts,
    "unscheduled_tasks": unscheduled_tasks
    }