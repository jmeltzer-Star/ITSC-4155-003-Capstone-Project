import os
import tempfile
import unittest
from datetime import datetime, timedelta

from backend.app import create_app


class ApiTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["DB_NAME"] = self.db_path

        with self.app.app_context():
            from backend.app.database import init_db
            init_db()

        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_and_list_tasks(self):
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

    def test_duration_based_scheduling(self):
        now = datetime.now()
        due_a = (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        due_b = (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")

        self.client.post("/api/tasks", json={
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

        self.client.post("/api/tasks", json={
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

        res = self.client.post("/api/schedule", json={
            "days": 1,
            "max_tasks_per_day": 5
        })

        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        schedule = data["schedule"]

        self.assertTrue(len(schedule) > 0)

        day = list(schedule.keys())[0]
        tasks = schedule[day]

        self.assertEqual(len(tasks), 2)

        task_a = tasks[0]
        task_b = tasks[1]

        self.assertEqual(task_a["scheduled_start"], "9:00 AM")
        self.assertEqual(task_a["scheduled_end"], "9:30 AM")

        self.assertEqual(task_b["scheduled_start"], "9:30 AM")
        self.assertEqual(task_b["scheduled_end"], "11:00 AM")

        self.assertEqual(task_a["scheduled_end"], task_b["scheduled_start"])


if __name__ == "__main__":
    unittest.main()