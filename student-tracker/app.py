from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date, timedelta

from dotenv import load_dotenv
import os

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

app = Flask(__name__)

cursor = db.cursor()

# 🏠 HOME PAGE
@app.route('/')
def home():
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    return render_template("home.html", subjects=subjects)


# ➕ ADD SUBJECT
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        is_major = request.form.get('is_major') == 'on'

        # limit 2 major subjects
        if is_major:
            cursor.execute("SELECT COUNT(*) FROM subjects WHERE is_major=1")
            count = cursor.fetchone()[0]
            if count >= 2:
                return "Only 2 major subjects allowed!"

        cursor.execute(
            "INSERT INTO subjects (name, is_major) VALUES (%s, %s)",
            (name, is_major)
        )
        db.commit()

        return redirect('/')

    return render_template('add_subject.html')


# 📖 ADD LOG
@app.route('/add_log/<int:subject_id>', methods=['GET', 'POST'])
def add_log(subject_id):
    if request.method == 'POST':
        hours = request.form['hours']
        notes = request.form['notes']
        completed = request.form.get('completed') == 'on'

        cursor.execute(
            "INSERT INTO study_logs (subject_id, date, hours, completed, notes) VALUES (%s, CURDATE(), %s, %s, %s)",
            (subject_id, hours, completed, notes)
        )
        db.commit()

        update_streak(subject_id)

        return redirect('/')

    return render_template('add_log.html', subject_id=subject_id)


# 🔥 STREAK SYSTEM
def update_streak(subject_id):
    cursor.execute("SELECT is_major FROM subjects WHERE id=%s", (subject_id,))
    is_major = cursor.fetchone()[0]

    if not is_major:
        return

    today = date.today()
    yesterday = today - timedelta(days=1)

    cursor.execute(
        "SELECT * FROM study_logs WHERE subject_id=%s AND date=%s AND completed=1",
        (subject_id, yesterday)
    )
    prev = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM streaks WHERE subject_id=%s",
        (subject_id,)
    )
    streak = cursor.fetchone()

    if prev:
        if streak:
            current = streak[1] + 1
            longest = max(streak[2], current)

            cursor.execute(
                "UPDATE streaks SET current_streak=%s, longest_streak=%s, last_updated=%s WHERE subject_id=%s",
                (current, longest, today, subject_id)
            )
        else:
            cursor.execute(
                "INSERT INTO streaks VALUES (%s, 1, 1, %s)",
                (subject_id, today)
            )
    else:
        if streak:
            cursor.execute(
                "UPDATE streaks SET current_streak=1, last_updated=%s WHERE subject_id=%s",
                (today, subject_id)
            )
        else:
            cursor.execute(
                "INSERT INTO streaks VALUES (%s, 1, 1, %s)",
                (subject_id, today)
            )

    db.commit()


# 📊 GRAPH ROUTE
@app.route('/graph')
def graph():
    cursor.execute(
        "SELECT date, SUM(hours) FROM study_logs GROUP BY date ORDER BY date"
    )
    data = cursor.fetchall()

    # convert date to string for JSON
    formatted_data = [(str(row[0]), float(row[1])) for row in data]

    return render_template("graph.html", data=formatted_data)


# 🎯 ADD GOAL
@app.route('/add_goal/<int:subject_id>', methods=['GET', 'POST'])
def add_goal(subject_id):
    if request.method == 'POST':
        goal_type = request.form['type']
        target = request.form['target']
        reward = request.form['reward']
        punishment = request.form['punishment']

        cursor.execute(
            "INSERT INTO goals (subject_id, type, target_hours, reward, punishment) VALUES (%s, %s, %s, %s, %s)",
            (subject_id, goal_type, target, reward, punishment)
        )
        db.commit()

        return redirect('/')

    return render_template("goals.html", subject_id=subject_id)


# 🚀 RUN
if __name__ == '__main__':
    app.run(debug=True)