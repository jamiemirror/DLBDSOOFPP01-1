"""Habit object oriented module defines Habit as object, requires direct access to db module"""
#imports
from datetime import datetime, date
#db access
from app.db import Database
#object creation
from dataclasses import dataclass

@dataclass
class Habit:
    """habit for tracking"""
    habit_id: int
    name: str
    desc: str
    interval: str
    current_streak: int = 0
    longest_streak: int = 0
    
    def __post_init__(self) -> None:
        """post initialization
        \
        check database entries to get habit's current_streak, longest_streak 
        """
        self.refreshStreaks()

    #compute streak
    def getStreaks(self, mode=None):
        """calculate streaks without resetting the saved values"""
        #check for mode BEFORE processing and save processing if matters!
        if not (mode is None or  mode == "c" or mode == "l"): 
            print("Unrecognized mode. Use 'c' for current streak, 'l' for longest streak or None.") 
        else:
            db = Database()
            history = [s for s in db.db["tables"]["history"] if s["habit_id"] == self.habit_id]
            if not history:
                return (0, 0) if mode is None else 0
            streaks = [record["streak"] for record in history]
            current_streak = streaks[-1] if streaks else 0
            longest_streak = max(streaks) if streaks else 0        
            if mode is None:
                return current_streak, longest_streak
            elif mode == "c":
                return current_streak
            elif mode == "l":
                return longest_streak
        
    def refreshStreaks(self):
        """method to re-calculate and assign the streak values"""
        self.current_streak, self.longest_streak = self.getStreaks() 
    
    def doesStreakContinue(self, last_date: str | date, current_date: datetime.date = None) -> bool:
        """check if the streak continues based on the habit's interval"""
        last_date = self.convertor(last_date) if isinstance(last_date, str) else last_date
        current_date = current_date or datetime.today().date()
        intervals = {"DAILY": 1, "WEEKLY": 7}
        interval_days = intervals.get(self.interval.upper(), 1)  
        return (current_date - last_date).days <= interval_days
    
    @staticmethod
    def convertor(date: str):
        """convert date in string 'YYYY-MM-DD' into a datetime.date object"""
        return datetime.strptime(date, "%Y-%m-%d").date()

    def getLastStreak(self) -> dict | None:
        """retrieve the last recorded streak for the habit"""
        db = Database()
        streaks = [s for s in db.db["tables"]["history"] if s["habit_id"] == self.habit_id]
        #empty case
        if not streaks:
            return None 
        return max(streaks, key=lambda s: self.convertor(s["date"]))
    
    def getAllStreaks(self) -> dict | None:
        """retrieve all recorded streaks for the habit"""
        db = Database()
        streaks = [s for s in db.db["tables"]["history"] if s["habit_id"] == self.habit_id]
        print(streaks)
        #empty case
        if not streaks:
            return None 
        return streaks
    
    def isChecked(self, date: str = None) -> bool:
        """check if a habit was completed on a specific date"""
        date = date or datetime.today().strftime('%Y-%m-%d')
        db = Database()
        return any(record["habit_id"] == self.habit_id and record["date"] == date for record in db.db["tables"]["history"])
    
    def getCheckins(self) -> list[str]:
        """retrieve all check-in dates, sorted"""
        db = Database()
        dates = [record["date"] for record in db.db["tables"]["history"] if record["habit_id"] == self.habit_id]
        dates.sort()
        return dates
    
    def checkOff(self):
        """mark habit as checked for today's date and updates streak history"""
        db = Database()
        today = datetime.today().strftime("%Y-%m-%d")
        if self.isChecked(today):
            print(f"Warning: Habit already checked off on {today}.")
            return False
        last_streak = self.getLastStreak()
        new_streak = 1
        if last_streak:
            if self.doesStreakContinue(last_streak["date"]):
                new_streak = last_streak["streak"] + 1
            else:
                last_streak["status"] = "broken"
                db.updateHistory(habit_id=self.habit_id, date=last_streak["date"], new_streak=last_streak["streak"], new_status=last_streak["status"])
        db.addHistory(habit_id=self.habit_id, streak=new_streak, status="active", date=today)
        db.saveDatabase()
        print("history: " + today + " added")
        self.refreshStreaks()
        return True
    
    def uncheckOff(self, date=None) -> bool:
        """remove a check-in for a given date (defaults to today)"""
        if not date:
            date = datetime.today().strftime('%Y-%m-%d')
        db = Database()
        #retrieve the last recorded streak
        last_streak = self.getLastStreak()
        #return False if no history exists for this habit
        if not last_streak or last_streak["date"] != date:
            print(f"Warning: check off not found for {date}.")
            return False
        #remove the habit entry for the given date
        db.deletefromHistory(habit_id=self.habit_id, date=date)
        return True

    @staticmethod
    def createfromJSON(data: dict):
        """create Habit object from JSON data"""
        return Habit(habit_id=int(data["id"]), name=data["name"], desc=data["desc"], interval=data["interval"])

    def savetoJSON(self):
        """convert Habit object to a dictionary"""
        return {"habit_id": self.habit_id, "name": self.name, "desc": self.desc, "interval": self.interval}
