"""Flask Application Router module used as middleware and backend for the web application 
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
from app.analytics import *
from app import app
from app import Database
from app import user

@app.route('/')
@app.route('/index')
def index(): 
    """main page for habits and analytics"""
    db_manager = Database()
    data = db_manager.db["tables"]["habit"]
    #convert JSON data into Habit objects
    habits = [Habit.createfromJSON(h) for h in data]  
    plot_long = plotLongestStreaks(habits)
    weekly = plotProgress(habits)
    return render_template("index.html", habits_weekly=filterHabits(habits, interval="WEEKLY"), habits_daily=filterHabits(habits, interval="DAILY"), plot_weekly_prog=weekly, plot_long=plot_long)

@app.route('/creator', methods=['GET', 'POST'])
def create_habit():
    """handle habit creation form and API requests"""
    db_manager = Database()
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            desc = data.get('desc', '')  #empty when omitted
            interval = data.get('interval').upper()
        else:
            name = request.form.get('name')
            desc = request.form.get('desc', '')
            interval = request.form.get('interval').upper()
        #required fields
        if not name or not interval:
            return jsonify({"error": "Habit name and interval are required!"}), 400
        try:
            habit_id = db_manager.addHabit(name=name, desc=desc, interval=interval)
            #JSON request
            if request.is_json:
                return jsonify({"message": "Habit created successfully!", "habit_id": habit_id}), 201
            #redirect to new habit page
            return redirect(url_for('habit', habit_id=habit_id))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return render_template('creator.html')

@app.route('/habit/<int:habit_id>') 
def habit(habit_id): 
    """all habit details"""
    db_manager = Database()
    habit_data = db_manager.getHabitByID(habit_id)
    if not habit_data:
        return "Habit not found", 404
    habit = Habit.createfromJSON(habit_data)
    current_streak, longest_streak = habit.getStreaks()
    #plots
    plot_history_html = plotHistory(habit)
    plot_stats_html = plotStats(habit)
    return render_template("habit.html", habit=habit, longest_streak=longest_streak, current_streak=current_streak, streaks= habit.getAllStreaks(), plot_history=plot_history_html, plot_stats=plot_stats_html)

@app.route("/api/habits")
def get_habits():
    """habits with optional filters: periodicity, min_streak"""
    db_manager = Database()
    habit_dicts = db_manager.db["tables"]["habit"]  #habit
    habits = [Habit.createfromJSON(h) for h in habit_dicts]  
    #get filter
    name = request.args.get("search", None)
    interval = request.args.get("interval", None)
    min_streak = request.args.get("streak", type=int, default=0)
    #get sorting
    sort_by = request.args.get("sort", type=str, default="none")
    reverse = request.args.get("reverse", False)
    #filter
    filtered_habits = filterHabits(habits=habits, name=name, interval=interval, min_streak=int(min_streak))
    print(sort_by + str(type(sort_by)))
    #reverse order
    if (sort_by == "none") and reverse :
        filtered_habits = sortHabits(habits=filtered_habits, by=None, reverse=reverse)
    #sort
    if (sort_by != "none"):
        accepted_sorts = ["name", "interval", "l", "c"]
        if sort_by in accepted_sorts:
            print("i sorted with accepted sort")
            filtered_habits = sortHabits(habits=filtered_habits, by=sort_by, reverse=reverse)
        else:
            filtered_habits = sortHabits(habits=filtered_habits, by=None, reverse=reverse)
    formatted_habits = [{"id": habit.habit_id, "name": habit.name, "desc": habit.desc, "interval": habit.interval, "streak": habit.longest_streak}
        for habit in filtered_habits
    ]
    return jsonify(formatted_habits)

@app.route("/habits")
def habit_list():
    return render_template("habits.html")

@app.route("/check/<int:habit_id>", methods=["POST"])
def check(habit_id):
    """check-off state of a habit"""
    db_manager = Database()
    #receive JSON data
    data = request.get_json()  
    is_checked = data.get("checked", False)
    print(f" Received POST for habit {habit_id} with checked: {is_checked}")
    habit_data = db_manager.getHabitByID(habit_id)  
    if not habit_data:
        print(f" Habit {habit_id} not found!")
        return jsonify({"error": "Habit not found"}), 404
    habit = Habit.createfromJSON(habit_data)
    if is_checked:
        #add date today
        habit.checkOff()
        print(f" Habit {habit.habit_id} checked off - New check_record: {habit.getLastStreak()}")
    else:
        #remove date today
        habit.uncheckOff()
        print(f" Habit {habit.habit_id} unchecked - Updated check_record: {habit.getLastStreak()}")
    return jsonify({"success": True, "check_record": habit.getLastStreak()})

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    """gets habit data by ID"""
    db_manager = Database()
    habit = db_manager.getHabitByID(habit_id)
    habit_obj = Habit.createfromJSON(habit)
    if not habit:
        return "Habit not found", 404
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("desc")
        interval = request.form.get("interval")
        habit["name"] = name
        habit["desc"] = desc
        habit["interval"] = interval
        if db_manager.updateHabit(habit_id=habit_id, name=habit["name"], desc=habit["desc"], interval=habit["interval"]) is None:
            print("failed update")
            return render_template("edit.html", habit=habit_obj)
        return redirect(url_for("habit", habit_id=habit_id))
    return render_template("edit.html", habit=habit_obj)

@app.route("/delete/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    """hardcoded user/admin to test inheritance and polymorphism 
    real use case with multi-user system after login
    sample usage c_user = user.User or c_user = user.Admin"""
    c_user = user.Admin
    if c_user.canDelete():
        db_manager = Database()
        if db_manager.getHabitByID(habit_id=habit_id):
            db_manager.deleteHabit(habit_id)
            return jsonify({"message": f"Habit {habit_id} deleted successfully"}), 200
        return jsonify({"error": "Habit not found"}), 404
    else:
        return jsonify({"error": "Only admin can delete habits!"}), 403

@app.route('/seed-data', methods=['POST'])
def seed_data():
    """seeding of habit data"""
    db = Database()
    result = db.get_seed_data()
    return redirect('/')  #redirect
