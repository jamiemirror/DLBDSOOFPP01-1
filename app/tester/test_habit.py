import pytest
from datetime import datetime, timedelta
from app.habit import Habit
from app.db import Database

@pytest.fixture
def setup_habit():
    """create habit"""
    db = Database()
    #init database
    db.db["tables"]["history"] = []
    db.saveDatabase()
    habit = Habit(habit_id=1, name="Test Habit", desc="Testing Habit", interval="DAILY")
    return habit, db

def test_habit_initialization(setup_habit):
    """init habit"""
    habit, _ = setup_habit
    assert habit.habit_id == 1
    assert habit.name == "Test Habit"
    assert habit.interval == "DAILY"
    assert habit.current_streak == 0
    assert habit.longest_streak == 0

def test_check_off_habit(setup_habit):
    """habit check-off/streak update"""
    habit, db = setup_habit
    assert habit.checkOff() is True
    assert habit.current_streak == 1
    assert habit.isChecked() is True

def test_streak_continuation(setup_habit):
    """streak continues/with periodicity"""
    habit, db = setup_habit
    today = datetime.today().strftime("%Y-%m-%d")
    #today
    habit.checkOff()  
    assert habit.current_streak == 1
    #next day check-off
    next_day = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    db.addHistory(habit.habit_id, 2, "active", next_day)
    db.saveDatabase()
    habit.refreshStreaks()
    assert habit.current_streak == 2

def test_uncheck_habit(setup_habit):
    """remove from habits history"""
    habit, _ = setup_habit
    habit.checkOff()
    #today
    assert habit.uncheckOff() is True  
    assert habit.isChecked() is False