"""database Model in JSON"""
#imports 
import json
import os
from datetime import datetime, timedelta
#use getSeedData() to populate empty Database   
import random
   
class Database:
    """manage JSON database with methods for load and query"""
    #two intervals validation 
    VALID_INTERVALS = {"DAILY", "WEEKLY"}
    def __init__(self, filename=None):
        """initial load"""
        self.filename = filename if filename else os.getcwd() + "\\app\\main.json"
        self.db_schema = {"database": self.filename, "tables": {"habit": [], "history": []}}
        self.db = self.loadDatabase()

    def saveDatabase(self):
        """save the current database to a JSON file"""
        with open(self.filename, "w") as f:
            json.dump(self.db, f, indent=4)

    def loadDatabase(self):
        """load the database from the file (or initializes if non-existing)"""
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.db = self.db_schema
            self.saveDatabase()
            return self.db

    def addHabit(self, name, desc, interval, id=None):
        """create new habit entry in the database
        \
        """
        #name check
        if self.getHabitByName(name):
            raise ValueError(f"Error: Habit '{name}' already exists!")
        #interval check
        if interval not in self.VALID_INTERVALS:
            raise ValueError(f"{interval}': must be " + ", ".join(self.VALID_INTERVALS))
        #adder
        habit_id = id or self.getNextID()
        new_habit = {"id": habit_id, "name": name, "desc": desc, "interval": interval}
        self.db["tables"]["habit"].append(new_habit)
        self.saveDatabase()
        return habit_id
    
    def addHistory(self, habit_id: int, streak: int, status: str, date: str):
        """add history entry for a habit"""
        self.db["tables"]["history"].append({"habit_id": habit_id, "streak": streak, "status": status, "date": date})
        self.saveDatabase()
        return True
    
    def getNextID(self):
        """return next available habit ID. Used for attaining appropraite habit id in addHabit()"""
        db_data = self.loadDatabase()
        if not db_data["tables"]["habit"]:
            return 0
        return max(habit["id"] for habit in db_data["tables"]["habit"]) + 1
    
    def getHabitByName(self, name):
        """return list of habits matching the name"""
        return [habit for habit in self.db["tables"]["habit"] if habit["name"] == name]

    def getHabitByID(self, habit_id) -> dict[str, any]:
        """return a habit by its ID"""
        for habit in self.db["tables"]["habit"]:
            if int(habit["id"]) == habit_id:
                return habit
        return None

    def deleteHabit(self, habit_id):
        """remove habit and its history"""
        habit_id = int(habit_id)
        try:
            self.db["tables"]["habit"] = [habit for habit in self.db["tables"]["habit"] if int(habit["id"]) != habit_id]
            self.db["tables"]["history"] = [record for record in self.db["tables"]["history"] if int(record["habit_id"]) != habit_id]
            self.saveDatabase()
        except Exception as e:
            return False, e
        return True

    def deletefromHistory(self, habit_id: int, date: str) -> bool:
        """remove specific habit record from history by habit_id and date"""
        initial_length = len(self.db["tables"]["history"])
        #filter 
        self.db["tables"]["history"] = [
            record for record in self.db["tables"]["history"]
            if not (record["habit_id"] == habit_id and record["date"] == date)
        ]
        if len(self.db["tables"]["history"]) < initial_length:
            self.saveDatabase()
            return True 
        return False
    
    def updateHabit(self, habit_id: int, name: str = None, desc: str = None, interval: str = None) -> bool:
        """update existing habit's attributes"""
        for habit in self.db["tables"]["habit"]:
            if habit["id"] == habit_id:
                if name:
                    habit["name"] = name
                if desc:
                    habit["desc"] = desc
                if interval:
                    if interval not in self.VALID_INTERVALS:
                        raise ValueError(f"Invalid interval '{interval}'. Valid choices: {', '.join(self.VALID_INTERVALS)}")
                    habit["interval"] = interval
                self.saveDatabase()
                print(name + " updated")
                return True 
        print(f"Warning: Habit with ID {habit_id} not found.")
        return False 

    def updateHistory(self, habit_id: int, date: str, new_streak: int, new_status: str) -> bool:
        """update existing history record with new streak and status"""
        for record in self.db["tables"]["history"]:
            if record["habit_id"] == habit_id and record["date"] == date:
                record["streak"] = new_streak
                record["status"] = new_status
                self.saveDatabase()
                return True
        print(f"Warning: No matching history record found for habit ID {habit_id} on {date}.")
        return False

    #seeding
    def get_seed_data(self):
        """populate database with 5 sets of weekly and daily predefined habits and 4 weeks of history for testing"""
        sample_habits = [
            ("Breakfast", "Prepare and eat breakfast", "DAILY"),
            ("Lunch", "Prepare and eat lunch", "DAILY"),
            ("Dinner", "Prepare and eat dinner", "DAILY"),
            ("Sleep", "Go to sleep at night", "DAILY"),
            ("Wake-up", "Wake-up at morning", "DAILY"),
            ("English breakfast", "Have sunday breakfast at the pub", "WEEKLY"),
            ("Lunch with friends", "Have sunday lunch with friends at the pub", "WEEKLY"),
            ("Family dinner", "Have family dinner with parents", "WEEKLY"),
            ("Sleepover", "Sleeopver at friend", "WEEKLY"),
            ("Wake-up at Monday", "Wake-up at Monday and go to work", "WEEKLY")
        ]

        #add habits
        for name, desc, interval in sample_habits:
            habit_id = self.addHabit(name, desc, interval)
            #generate history records
            start_date = datetime.today() - timedelta(weeks=4)
            streak = 0
            for i in range(20 + random.randint(0, 7)):
                date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                #add random habit breaks
                if random.random() > 0.85: 
                    continue
                if random.random() > 0.9: 
                    status = "broken"
                    streak = 0 
                else:
                    status = "active"
                    streak += random.choice([1, 1, 1, 2])
                self.addHistory(habit_id, streak, status, date_str)
        self.saveDatabase()
        print("All habits were added.")
        #reload main page
        return {"status": "success", "redirect": "/main"}
