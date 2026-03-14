import unittest
from app import create_app


class TestMomentumScheduler(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_create_task_api(self):
        response = self.app.post("/api/tasks", json={
            "title": "Finish Report",
            "due_date": "2026-03-20 12:00",
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": None,
            "category": "School"
        })

        self.assertEqual(response.status_code, 200)

    def test_create_task_missing_title(self):
        response = self.app.post("/api/tasks", json={
            "title": "",
            "due_date": "2026-03-20 12:00",
            "priority": "High",
            "duration_minutes": 60,
            "effort_level": "Medium",
            "start_after": None,
            "category": "School"
        })

        self.assertNotEqual(response.status_code, 200)

    def test_generate_schedule_api(self):
        response = self.app.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 3
        })

        self.assertEqual(response.status_code, 200)

    def test_schedule_daily_limit(self):
        response = self.app.post("/api/schedule", json={
            "days": 7,
            "max_tasks_per_day": 2
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("schedule", data)

    def test_delete_task_api(self):
        create_response = self.app.post("/api/tasks", json={
            "title": "Delete Me",
            "due_date": "2026-03-22 10:00",
            "priority": "Low",
            "duration_minutes": 30,
            "effort_level": "Low",
            "start_after": None,
            "category": "General"
        })

        created_task = create_response.get_json()
        task_id = created_task["id"]

        delete_response = self.app.delete(f"/api/tasks/{task_id}")
        self.assertEqual(delete_response.status_code, 200)

    def test_update_task_api(self):
        create_response = self.app.post("/api/tasks", json={
            "title": "Old Task",
            "due_date": "2026-03-22 10:00",
            "priority": "Low",
            "duration_minutes": 30,
            "effort_level": "Low",
            "start_after": None,
            "category": "General"
        })

        created_task = create_response.get_json()
        task_id = created_task["id"]

        update_response = self.app.put(f"/api/tasks/{task_id}", json={
            "title": "Updated Task",
            "due_date": "2026-03-22 12:00",
            "priority": "High",
            "status": "Pending",
            "duration_minutes": 60,
            "effort_level": "High",
            "start_after": None,
            "category": "Work"
        })

        self.assertEqual(update_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()