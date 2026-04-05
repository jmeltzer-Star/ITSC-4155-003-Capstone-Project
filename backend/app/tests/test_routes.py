import os
import tempfile
import unittest
from datetime import datetime, timedelta

from backend.app import create_app


'''
    This File Contains all Our Application Testing -- Ranging from Unit Testing, to Integrated Testing, and BlackBox Testing
    They are Organized Based on the Tests in Sections Below


'''

class ApiTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["DB_NAME"] = self.db_path
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SESSION_COOKIE_HTTPONLY"] = False

        with self.app.app_context():
            from backend.app.database import init_db
            init_db()

        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login(self):
        return self.client.post("/api/login", json={
            "username": "admin",
            "password": "momentum123"
        })

    def test_create_and_list_tasks(self):
        self.login()

        res = self.client.post("/api/tasks", json={
            "title": "Math Homework",
            "due_date": "2026-03-01 23:59",
            "priority": "High"
        })

        self.assertEqual(res.status_code, 201)

        res = self.client.get("/api/tasks")
        self.assertEqual(res.status_code, 200)

        data = res.get_json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Math Homework")
        self.assertEqual(data[0]["status"], "Pending")
        self.assertEqual(data[0]["due_date"], "2026-03-01 23:59")
        self.assertEqual(data[0]["priority"], "High")

    def test_edit_task(self):
        self.login()

        res = self.client.post("/api/tasks", json={
            "title": "Finish Sprint Report",
            "due_date": "2026-03-10 17:00",
            "priority": "High"
        })

        task = res.get_json()
        task_id = task["id"]

        res = self.client.put(f"/api/tasks/{task_id}", json={
            "title": "Finish Sprint Report (Updated)",
            "due_date": "2026-03-12 12:00",
            "priority": "Medium",
            "status": "Not Started",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })

        self.assertEqual(res.status_code, 200)

        res = self.client.get("/api/tasks")
        data = res.get_json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Finish Sprint Report (Updated)")
        self.assertEqual(data[0]["priority"], "Medium")
        self.assertEqual(data[0]["status"], "Not Started")

    def test_delete_task(self):
        self.login()

        res = self.client.post("/api/tasks", json={
            "title": "Task To Delete",
            "due_date": "2026-04-01 12:00",
            "priority": "Low"
        })

        task = res.get_json()
        task_id = task["id"]

        res = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(res.status_code, 200)

        res = self.client.get("/api/tasks")
        data = res.get_json()

        self.assertEqual(len(data), 0)

    # User Story #4: Generate Schedule From Task Log
    def test_generate_schedule_with_no_tasks(self):
        self.login()

        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 4
        })

        self.assertEqual(res.status_code, 200)

        data = res.get_json()

        self.assertEqual(data["message"], "No tasks available to schedule.")
        self.assertEqual(data["schedule"], {})

    def test_generate_schedule_sorts_by_due_date_and_priority(self):
        self.login()

        now = datetime.now()

        same_due = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        later_due = (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")

        # Higher priority, earlier due date
        self.client.post("/api/tasks", json={
            "title": "Task A",
            "due_date": same_due,
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })

        # Lower priority, same due date
        self.client.post("/api/tasks", json={
            "title": "Task B",
            "due_date": same_due,
            "priority": "Low",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })

        # Later due date
        self.client.post("/api/tasks", json={
            "title": "Task C",
            "due_date": later_due,
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })

        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 5
        })

        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        schedule = data["schedule"]

        self.assertTrue(len(schedule) > 0)

        first_day = list(schedule.keys())[0]
        tasks = schedule[first_day]

        self.assertEqual(tasks[0]["title"], "Task A")
        self.assertEqual(tasks[1]["title"], "Task B")
        self.assertEqual(tasks[2]["title"], "Task C")

    
    # Tests that tasks overflow to the next day when daily limit is reached

    def test_schedule_overflow_to_next_day(self):
        self.login()

        now = datetime.now()

        for i in range(3):
            due_date = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

            self.client.post("/api/tasks", json={
                "title": f"Overflow Task {i}",
                "due_date": due_date,
                "priority": "High",
                "duration_minutes": 60,
                "effort_level": "Medium",
                "start_after": "",
                "category": "General",
                "description": "",
                "notes": ""
            })

        res = self.client.post("/api/schedule", json={
            "days": 3,
            "max_tasks_per_day": 1
        })

        self.assertEqual(res.status_code, 200)

        schedule = res.get_json()["schedule"]
        days = list(schedule.keys())

        self.assertEqual(len(schedule[days[0]]), 1)
        self.assertEqual(len(schedule[days[1]]), 1)


    
    # Tests that tasks are not scheduled before their start_after time
    
    def test_start_after_prevents_early_scheduling(self):
        self.login()

        future_start = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
        due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        self.client.post("/api/tasks", json={
            "title": "Future Locked Task",
            "due_date": due_date,
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": future_start,
            "category": "General",
            "description": "",
            "notes": ""
        })

        res = self.client.post("/api/schedule", json={
            "days": 5,
            "max_tasks_per_day": 2
        })

        self.assertEqual(res.status_code, 200)

        schedule = res.get_json()["schedule"]

        all_tasks = []
        for day in schedule.values():
            all_tasks.extend(day)

        self.assertEqual(len(all_tasks), 0)

    
    def test_duration_based_scheduling(self):
        self.login()

        tomorrow = datetime.now().date() + timedelta(days=1)
        due_date = datetime.combine(
        tomorrow,
        datetime.strptime("3:00 PM", "%I:%M %p").time()
        ).strftime("%Y-%m-%d %H:%M")

        res = self.client.post("/api/tasks", json={
        "title": "Long Task",
        "due_date": due_date,
        "priority": "High",
        "duration_minutes": 120,
        "effort_level": "Medium",
        "start_after": "",
        "category": "General",
        "description": "",
        "notes": ""
        })
        self.assertEqual(res.status_code, 201)

        schedule_res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 5
        })
        self.assertEqual(schedule_res.status_code, 200)

        schedule = schedule_res.get_json()["schedule"]
        self.assertTrue(len(schedule) > 0)

        day = list(schedule.keys())[0]
        tasks = schedule[day]

        self.assertEqual(len(tasks), 1)

        task = tasks[0]
        self.assertEqual(task["scheduled_start"], "9:00 AM")
        self.assertEqual(task["scheduled_end"], "11:00 AM")

    def time_to_minutes(self, time_str):
        time_part, meridiem = time_str.split(" ")
        hours, minutes = map(int, time_part.split(":"))

        if meridiem == "PM" and hours != 12:
            hours += 12
        if meridiem == "AM" and hours == 12:
            hours = 0

        return hours * 60 + minutes

    # User Story #5: Conflict Detection
    def find_conflicts_in_schedule(self, schedule):
        conflicts = []

        for day_key, tasks in schedule.items():
            for i in range(len(tasks)):
                first = tasks[i]
                first_start = self.time_to_minutes(first["scheduled_start"])
                first_end = self.time_to_minutes(first["scheduled_end"])

                for j in range(i + 1, len(tasks)):
                    second = tasks[j]
                    second_start = self.time_to_minutes(second["scheduled_start"])
                    second_end = self.time_to_minutes(second["scheduled_end"])

                    overlaps = first_start < second_end and second_start < first_end

                    if overlaps:
                        conflicts.append({
                            "day": day_key,
                            "first": first,
                            "second": second,
                            "suggested_next_slot": first["scheduled_end"]
                        })

        return conflicts

    def test_conflict_detection_story(self):
        """
        USER STORY: Conflict Detection

        As a user, I want conflicts detected in my schedule
        so that tasks do not overlap.
        """

        self.login()

        conflict_schedule = {
            "2026-03-25": [
                {
                    "id": 1,
                    "title": "Task A",
                    "scheduled_start": "2:00 PM",
                    "scheduled_end": "3:00 PM"
                },
                {
                    "id": 2,
                    "title": "Task B",
                    "scheduled_start": "2:30 PM",
                    "scheduled_end": "3:30 PM"
                }
            ]
        }

        conflicts = self.find_conflicts_in_schedule(conflict_schedule)

        # AC 1 + AC 2:
        # overlapping scheduled task times are detected automatically
        self.assertEqual(len(conflicts), 1)

        # AC 3:
        # suggested next available slot is shown
        self.assertEqual(conflicts[0]["suggested_next_slot"], "3:00 PM")

        # AC 4:
        # verify the two overlapping tasks are the ones identified
        self.assertEqual(conflicts[0]["first"]["title"], "Task A")
        self.assertEqual(conflicts[0]["second"]["title"], "Task B")

    def test_no_conflict_detection_story(self):
        """
        USER STORY: No Conflict Case

        Given no overlapping task times exist,
        the system should detect no conflicts.
        """

        self.login()

        no_conflict_schedule = {
            "2026-03-25": [
                {
                    "id": 1,
                    "title": "Task A",
                    "scheduled_start": "2:00 PM",
                    "scheduled_end": "3:00 PM"
                },
                {
                    "id": 2,
                    "title": "Task B",
                    "scheduled_start": "3:00 PM",
                    "scheduled_end": "4:00 PM"
                }
            ]
        }

        conflicts = self.find_conflicts_in_schedule(no_conflict_schedule)

        # AC 5:
        # no overlap means no conflict detected
        self.assertEqual(len(conflicts), 0)

    # User Story #58 -- Schedule Auto Refresh
    def test_schedule_reflects_latest_task_changes(self):
        """
        USER STORY: Schedule Auto Refresh
        """

        self.login()

        now = datetime.now()
        due_date = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        # 1. Empty state
        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 4
        })

        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["message"], "No tasks available to schedule.")
        self.assertEqual(data["schedule"], {})

        # 2. Create task
        create_res = self.client.post("/api/tasks", json={
            "title": "Task A",
            "due_date": due_date,
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": "",
            "category": "General",
            "description": "Original description",
            "notes": "Original notes"
        })

        self.assertEqual(create_res.status_code, 201)
        task_id = create_res.get_json()["id"]

        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 4
        })

        schedule = res.get_json()["schedule"]
        self.assertTrue(len(schedule) > 0)

        all_titles = [task["title"] for day in schedule.values() for task in day]
        self.assertIn("Task A", all_titles)

        # 3. Edit task
        edit_res = self.client.put(f"/api/tasks/{task_id}", json={
            "title": "Task A Updated",
            "due_date": due_date,
            "priority": "Medium",
            "status": "Not Started",
            "duration_minutes": 90,
            "effort_level": "High",
            "start_after": "",
            "category": "School",
            "description": "Updated description",
            "notes": "Updated notes"
        })

        self.assertEqual(edit_res.status_code, 200)

        schedule = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 4
        }).get_json()["schedule"]

        updated = None
        for day in schedule.values():
            for task in day:
                if task["title"] == "Task A Updated":
                    updated = task
                    break

        self.assertIsNotNone(updated)
        self.assertEqual(updated["priority"], "Medium")
        self.assertEqual(updated["duration_minutes"], 90)

        # 4. Delete task
        delete_res = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(delete_res.status_code, 200)

        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 4
        })

        data = res.get_json()
        self.assertEqual(data["message"], "No tasks available to schedule.")
        self.assertEqual(data["schedule"], {})

    def test_task_duration_scheduling_story(self):
        """
        USER STORY: Task Duration Scheduling
        """

        self.login()

        tomorrow = datetime.now().date() + timedelta(days=1)
        due_a = datetime.combine(tomorrow, datetime.strptime("12:00", "%H:%M").time()).strftime("%Y-%m-%d %H:%M")
        due_b = datetime.combine(tomorrow, datetime.strptime("3:00 PM", "%I:%M %p").time()).strftime("%Y-%m-%d %H:%M")

        res_a = self.client.post("/api/tasks", json={
        "title": "Task A",
        "due_date": due_a,
        "priority": "High",
        "duration_minutes": 30,
        "effort_level": "Medium",
        "start_after": "",
        "category": "General",
        "description": "",
        "notes": ""
        })
        self.assertEqual(res_a.status_code, 201)

        res_b = self.client.post("/api/tasks", json={
        "title": "Task B",
        "due_date": due_b,
        "priority": "Medium",
        "duration_minutes": 90,
        "effort_level": "Medium",
        "start_after": "",
        "category": "General",
        "description": "",
        "notes": ""
        })
        self.assertEqual(res_b.status_code, 201)

        res = self.client.post("/api/schedule", json={
        "days": 7,
        "max_tasks_per_day": 5
        })
        self.assertEqual(res.status_code, 200)

        schedule = res.get_json()["schedule"]
        self.assertTrue(len(schedule) > 0)

        day = list(schedule.keys())[0]
        tasks = schedule[day]

        self.assertEqual(len(tasks), 2)

        task_a, task_b = tasks

        self.assertEqual(task_a["scheduled_start"], "9:00 AM")
        self.assertEqual(task_a["scheduled_end"], "9:30 AM")

        self.assertEqual(task_b["scheduled_start"], "9:30 AM")
        self.assertEqual(task_b["scheduled_end"], "11:00 AM")

        self.assertEqual(task_a["scheduled_end"], task_b["scheduled_start"])

    def to_minutes(time_str):
        time_part, meridiem = time_str.split(" ")
        hours, minutes = map(int, time_part.split(":"))
        if meridiem == "PM" and hours != 12:
            hours += 12
        if meridiem == "AM" and hours == 12:
            hours = 0
        return hours * 60 + minutes

        task_a_length = to_minutes(task_a["scheduled_end"]) - to_minutes(task_a["scheduled_start"])
        task_b_length = to_minutes(task_b["scheduled_end"]) - to_minutes(task_b["scheduled_start"])

        self.assertEqual(task_a_length, 30)
        self.assertEqual(task_b_length, 90)
        self.assertGreater(task_b_length, task_a_length)    

    def test_effort_level_scheduling_story(self):
        """
        USER STORY: Effort Level Scheduling

        As a user, I want tasks with higher effort levels
        to be prioritized when generating a schedule so that
        more demanding tasks are handled earlier.
        """

        self.login()

        now = datetime.now()
        same_due = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        # Task A: High effort
        res_a = self.client.post("/api/tasks", json={
            "title": "Task A",
            "due_date": same_due,
            "priority": "Medium",
            "duration_minutes": 60,
            "effort_level": "High",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })
        self.assertEqual(res_a.status_code, 201)

        # Task B: Low effort
        res_b = self.client.post("/api/tasks", json={
            "title": "Task B",
            "due_date": same_due,
            "priority": "Medium",
            "duration_minutes": 60,
            "effort_level": "Low",
            "start_after": "",
            "category": "General",
            "description": "",
            "notes": ""
        })
        self.assertEqual(res_b.status_code, 201)

        # Generate schedule
        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 5
        })
        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        schedule = data["schedule"]

        self.assertTrue(len(schedule) > 0)

        # Flatten all scheduled tasks in order
        scheduled_tasks = []
        for day_tasks in schedule.values():
            scheduled_tasks.extend(day_tasks)

        self.assertEqual(len(scheduled_tasks), 2)

        # AC 1 + AC 2:
        # Same due date + same priority -> higher effort first
        self.assertEqual(scheduled_tasks[0]["title"], "Task A")
        self.assertEqual(scheduled_tasks[0]["effort_level"], "High")
        self.assertEqual(scheduled_tasks[1]["title"], "Task B")
        self.assertEqual(scheduled_tasks[1]["effort_level"], "Low")

    def test_daily_task_limit_with_fewer_tasks_than_limit(self):
        self.login()

        now = datetime.now()

        for i in range(2):
            due_date = (now + timedelta(days=1, hours=i)).strftime("%Y-%m-%d %H:%M")

            res = self.client.post("/api/tasks", json={
                "title": f"Small Task {i + 1}",
                "due_date": due_date,
                "priority": "Medium",
                "duration_minutes": 60,
                "effort_level": "Medium",
                "start_after": "",
                "category": "General",
                "description": "",
                "notes": ""
            })

            self.assertEqual(res.status_code, 201)

        res = self.client.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 3
        })

        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        schedule = data["schedule"]

        day_keys = sorted(schedule.keys())
        self.assertEqual(len(schedule[day_keys[0]]), 2)

        for day_key, tasks in schedule.items():
            self.assertLessEqual(len(tasks), 3)

    
    
    
    
    
    ########## THis Section is More of Our Integrated Tests ##########
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     #Thse Our Integrated Tests -- Create then Get Tasks        

    def test_create_task_then_get_tasks(self):
        self.login()
        create_res = self.client.post("/api/tasks", json={
        "title": "Study Networking",
        "due_date": "2026-04-10 18:00",
        "priority": "High",
        "duration_minutes": 60,
        "effort_level": "High",
        "start_after": None,
        "category": "School",
        "description": "Review chapters",
        "notes": "Focus on routing"
    })

        self.assertEqual(create_res.status_code, 201)

        get_res = self.client.get("/api/tasks")
        self.assertEqual(get_res.status_code, 200)

        tasks = get_res.get_json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Study Networking")
        self.assertEqual(tasks[0]["priority"], "High")


    #Intgerated Test #2 -- Edit Then Get Updated Tasks in Schedule        

    def test_edit_task_then_get_updated_task(self):
        self.login()
        create_res = self.client.post("/api/tasks", json={
        "title": "Old Title",
        "due_date": "2026-04-10 18:00",
        "priority": "Medium",
        "duration_minutes": 60,
        "effort_level": "Medium",
        "start_after": None,
        "category": "General",
        "description": "",
        "notes": ""
    })
        self.assertEqual(create_res.status_code, 201)

        task_id = create_res.get_json()["id"]

        update_res = self.client.put(f"/api/tasks/{task_id}", json={
        "title": "Updated Title",
        "due_date": "2026-04-11 19:00",
        "priority": "High",
        "status": "In Progress",
        "duration_minutes": 90,
        "effort_level": "High",
        "start_after": None,
        "category": "School",
        "description": "Updated description",
        "notes": "Updated notes"
    })
        self.assertEqual(update_res.status_code, 200)

        get_res = self.client.get("/api/tasks")
        tasks = get_res.get_json()

        updated_task = next(t for t in tasks if t["id"] == task_id)
        self.assertEqual(updated_task["title"], "Updated Title")
        self.assertEqual(updated_task["priority"], "High")
        self.assertEqual(updated_task["status"], "In Progress")

    
    #Integrate #3 -- Delete Task + Confirms This is not in the schedule anymore
    def test_delete_task_then_confirm_removed(self):
        self.login()
        create_res = self.client.post("/api/tasks", json={
        "title": "Delete Me",
        "due_date": "2026-04-10 18:00",
        "priority": "Low",
        "duration_minutes": 30,
        "effort_level": "Low",
        "start_after": None,
        "category": "Personal",
        "description": "",
        "notes": ""
    })
        self.assertEqual(create_res.status_code, 201)

        task_id = create_res.get_json()["id"]

        delete_res = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(delete_res.status_code, 200)

        get_res = self.client.get("/api/tasks")
        tasks = get_res.get_json()

        self.assertFalse(any(t["task_id"] == task_id for t in tasks))

    
    #Intgegrates Test #4: Creating Schedule with Different Priorities
    def test_schedule_prioritizes_higher_effort_when_due_date_and_priority_match(self):
        self.login()

        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        self.client.post("/api/tasks", json={
        "title": "High Effort Task",
        "due_date": future_date,
        "priority": "Medium",
        "duration_minutes": 60,
        "effort_level": "High",
        "start_after": None,
        "category": "School",
        "description": "",
        "notes": ""
        })

        self.client.post("/api/tasks", json={
        "title": "Low Effort Task",
        "due_date": future_date,
        "priority": "Medium",
        "duration_minutes": 60,
        "effort_level": "Low",
        "start_after": None,
        "category": "School",
        "description": "",
        "notes": ""
        })

        schedule_res = self.client.post("/api/schedule", json={
        "days": 7,
        "max_tasks_per_day": 4
        })

        self.assertEqual(schedule_res.status_code, 200)
        data = schedule_res.get_json()

        schedule = data.get("schedule", {})
        all_scheduled = []
        for day_tasks in schedule.values():
            all_scheduled.extend(day_tasks)

        titles = [task["title"] for task in all_scheduled]

        self.assertIn("High Effort Task", titles)
        self.assertIn("Low Effort Task", titles)

        self.assertLess(
        titles.index("High Effort Task"),
        titles.index("Low Effort Task")
    )

    # ========================================================
# BLACK BOX TESTING / EQUIVALENCE PARTITIONING
# ========================================================

    def test_bb_create_task_valid_partition(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        res = self.client.post("/api/tasks", json={
        "title": "Math Homework",
        "due_date": future_date,
        "priority": "High",
        "duration_minutes": 60,
        "effort_level": "Medium",
        "start_after": None,
        "category": "School",
        "description": "Chapter 5 problems",
        "notes": "Bring calculator"
        })

        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("id", data)


    def test_bb_create_task_invalid_empty_title(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        res = self.client.post("/api/tasks", json={
        "title": "",
        "due_date": future_date,
        "priority": "High",
        "duration_minutes": 60,
        "effort_level": "Medium",
        "start_after": None,
        "category": "School",
        "description": "",
        "notes": ""
        })

        self.assertNotEqual(res.status_code, 201)




    def test_bb_create_task_invalid_duration_zero(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        res = self.client.post("/api/tasks", json={
        "title": "Bad Duration",
        "due_date": future_date,
        "priority": "Medium",
        "duration_minutes": 0,
        "effort_level": "Low",
        "start_after": None,
        "category": "General",
        "description": "",
        "notes": ""
        })

        self.assertNotEqual(res.status_code, 201)


    def test_bb_edit_task_valid_partition(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        updated_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")

        create_res = self.client.post("/api/tasks", json={
        "title": "Original Task",
        "due_date": future_date,
        "priority": "Medium",
        "duration_minutes": 60,
        "effort_level": "Medium",
        "start_after": None,
        "category": "General",
        "description": "",
        "notes": ""
        })

        self.assertEqual(create_res.status_code, 201)
        task_id = create_res.get_json()["id"]

        update_res = self.client.put(f"/api/tasks/{task_id}", json={
        "title": "Updated Task",
        "due_date": updated_date,
        "priority": "High",
        "status": "In Progress",
        "duration_minutes": 90,
        "effort_level": "High",
        "start_after": None,
        "category": "School",
        "description": "Updated description",
        "notes": "Updated notes"
        })

        self.assertEqual(update_res.status_code, 200)


    def test_bb_delete_task_valid_partition(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        create_res = self.client.post("/api/tasks", json={
        "title": "Delete Me",
        "due_date": future_date,
        "priority": "Low",
        "duration_minutes": 30,
        "effort_level": "Low",
        "start_after": None,
        "category": "Personal",
        "description": "",
        "notes": ""
        })

        self.assertEqual(create_res.status_code, 201)
        task_id = create_res.get_json()["id"]

        delete_res = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(delete_res.status_code, 200)


    def test_bb_delete_task_invalid_nonexistent_id(self):
        self.login()

        res = self.client.delete("/api/tasks/999999")
        self.assertNotEqual(res.status_code, 200)


    def test_bb_search_valid_partial_title_partition(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        self.client.post("/api/tasks", json={
        "title": "Math Homework",
        "due_date": future_date,
        "priority": "High",
        "duration_minutes": 60,
        "effort_level": "Medium",
        "start_after": None,
        "category": "School",
        "description": "Algebra",
        "notes": "Unit 3"
            })

        res = self.client.get("/api/tasks")
        self.assertEqual(res.status_code, 200)

        tasks = res.get_json()
        filtered = [t for t in tasks if "math" in t["title"].lower()]

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["title"], "Math Homework")


    def test_bb_schedule_valid_partition(self):
        self.login()

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        self.client.post("/api/tasks", json={
        "title": "Task A",
        "due_date": future_date,
        "priority": "High",
        "duration_minutes": 60,
        "effort_level": "High",
        "start_after": None,
        "category": "School",
        "description": "",
        "notes": ""
        })

        res = self.client.post("/api/schedule", json={
        "days": 7,
        "max_tasks_per_day": 4
        })

        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("schedule", data)


    def test_bb_schedule_invalid_max_tasks_partition(self):
        self.login()

        res = self.client.post("/api/schedule", json={
        "days": 7,
        "max_tasks_per_day": 0
        })

        self.assertEqual(res.status_code, 400)


    





if __name__ == "__main__":
    unittest.main()
