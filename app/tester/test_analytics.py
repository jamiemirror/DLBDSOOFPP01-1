import pytest
from datetime import datetime, timedelta
from app.habit import Habit
from app.db import Database
from app.analytics import (parseDates, getProgress, getFullProgress, filterHabits, sortHabits, plotLongestStreaks, plotHistory, plotStats, plotProgress)

@pytest.fixture
def sample_habits():
    """sample habits"""
    habits = [
        Habit(habit_id=1, name="Breakfast", desc="Morning breakfast", interval="DAILY"),
        Habit(habit_id=2, name="Dinner", desc="Dinner at evening", interval="DAILY"),
        Habit(habit_id=3, name="Sleepover", desc="", interval="WEEKLY")
    ]
    return habits

def test_parseDates():
    """date string conversion to datetime"""
    dates = ["2026-03-01", "2026-03-02"]
    parsed_dates = parseDates(dates)
    assert all(isinstance(date, datetime) for date in parsed_dates)

def test_getProgress(sample_habits):
    """habit progress for a given date"""
    date = datetime.today().strftime('%Y-%m-%d')
    sample_habits[0].checkOff()
    progress = getProgress(sample_habits, date)
    assert 0 <= progress <= 100

def test_getFullProgress(sample_habits):
    """full progress history"""
    sample_habits[0].checkOff()
    progress_history = getFullProgress(sample_habits)
    assert isinstance(progress_history, dict)

def test_filterHabits(sample_habits):
    """filter habits by name, interval and streak length"""
    filtered = filterHabits(sample_habits, interval="DAILY")
    assert all(h.interval == "DAILY" for h in filtered)

def test_sortHabits(sample_habits):
    """sort habits by name and streak value"""
    sorted_habits = sortHabits(sample_habits, by="name")
    assert sorted_habits[0].name == "Breakfast"

def test_plotLongestStreaks(sample_habits):
    """generation of longest streaks"""
    plot_html = plotLongestStreaks(sample_habits)
    assert "<div" in plot_html

def test_plotHistory(sample_habits):
    """habit history"""
    sample_habits[0].checkOff()
    plot_html = plotHistory(sample_habits[0])
    assert "<div" in plot_html

def test_plotStats(sample_habits):
    """habit check-off statistics"""
    sample_habits[0].checkOff()
    plot_html = plotStats(sample_habits[0])
    assert "<div" in plot_html

def test_plotProgress(sample_habits):
    """habits progress"""
    sample_habits[0].checkOff()
    plot_html = plotProgress(sample_habits)
    assert "<div" in plot_html
