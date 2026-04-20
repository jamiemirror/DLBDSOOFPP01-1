import unittest
import os
import json
from datetime import datetime
from app.db import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """createtemporary database"""
        self.test_db_file = "test_db.json"
        self.db = Database(self.test_db_file)
        self.db.db = {  
            "database": self.test_db_file,
            "tables": {"habit": [], "history": []}
        }
        self.db.saveDatabase()

    def tearDown(self):
        """delete temporary database"""
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_addHabit(self):
        """add habit"""
        habit_id = self.db.addHabit("Breakfast", "Morning breakfast", "DAILY")
        habit = self.db.getHabitByID(habit_id)
        self.assertIsNotNone(habit)
        self.assertEqual(habit["name"], "Breakfast")
        self.assertEqual(habit["interval"], "DAILY")

    def test_addHabit_duplicate(self):
        """add duplicate habit to raise error"""
        self.db.addHabit("Lunch", "Have a lunch", "DAILY")
        with self.assertRaises(ValueError):
            self.db.addHabit("Lunch", "Have a lunch", "DAILY")

    def test_addHistory(self):
        """add habit history"""
        habit_id = self.db.addHabit("Sleep", "Nighly sleep", "DAILY")
        result = self.db.addHistory(habit_id, 3, "active", "2026-03-16")
        self.assertTrue(result)
        history = [h for h in self.db.db["tables"]["history"] if h["habit_id"] == habit_id]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["status"], "active")

    def test_deleteHabit(self):
        """delete habit with all history, normally only for administrator"""
        habit_id = self.db.addHabit("Dinner", "Dinner at evening", "WEEKLY")
        self.db.addHistory(habit_id, 5, "active", "2026-03-10")
        result = self.db.deleteHabit(habit_id)
        self.assertTrue(result)
        self.assertIsNone(self.db.getHabitByID(habit_id))
        self.assertEqual(len(self.db.db["tables"]["history"]), 0)

    def test_updateHabit(self):
        """update habit"""
        habit_id = self.db.addHabit("Wake-up", "Wake-up at morning", "DAILY")
        self.db.updateHabit(habit_id, name="Wake-up", desc="Wake-up late")
        habit = self.db.getHabitByID(habit_id)
        self.assertEqual(habit["name"], "Wake-up")
        self.assertEqual(habit["desc"], "Wake-up late")

    def test_updateHistory(self):
        """update history"""
        habit_id = self.db.addHabit("Breakfast", "Morning breakfast", "DAILY")
        self.db.addHistory(habit_id, 2, "active", "2026-03-14")
        self.db.updateHistory(habit_id, "2026-03-14", 3, "active")
        history = [h for h in self.db.db["tables"]["history"] if h["habit_id"] == habit_id]
        self.assertEqual(history[0]["streak"], 3)

if __name__ == "__main__":
    unittest.main()
