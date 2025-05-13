from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import re
import os
import collections

app = Flask(__name__)
mood_entries = []  # Store mood logs here

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'test@mindmate.com' and password == '1234':
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"New user signed up: {email} ({password})")  # Dummy print
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/mood-tracker')
def mood_tracker():
    return render_template('mood_tracker.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ✅ STATIC CHATBOT - No API, simple rule-based responses
@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_input = request.json.get("message", "").lower()

    if "sad" in user_input or "depressed" in user_input:
        reply = "I'm really sorry you're feeling this way 💙 You're not alone. Want to talk more about it?"
    elif "happy" in user_input or "excited" in user_input:
        reply = "Yay! That’s amazing to hear 😊 Tell me more about what’s making you happy!"
    elif "anxious" in user_input or "worried" in user_input:
        reply = "It's okay to feel anxious sometimes. Try taking a deep breath 🌿 I'm here to listen."
    elif "angry" in user_input:
        reply = "It's valid to feel angry. Want to share what's bothering you?"
    elif "hello" in user_input or "hi" in user_input:
        reply = "Hey there! 👋 How are you feeling today?"
    else:
        reply = "I'm here for you ❤️ Tell me more about what you're going through."

    return jsonify({"reply": reply})

# ✅ Save Mood Entry
@app.route('/api/mood', methods=['POST'])
def save_mood():
    data = request.get_json()
    mood = data.get("mood")
    note = data.get("note", "")
    now = datetime.now()
    mood_entries.append({
        "date": now,
        "mood": mood,
        "note": note
    })
    return jsonify({"message": "Mood saved successfully"})

# ✅ Return Mood Data for Dashboard/Insights
@app.route('/api/mood-data')
def mood_data():
    dist = collections.Counter(e['mood'] for e in mood_entries)

    rating_map = {'Great':5, 'Good':4, 'Okay':3, 'Bad':2, 'Terrible':1}
    today = datetime.now().date()
    weekly = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily = [rating_map[e['mood']] for e in mood_entries if e['date'].date() == day]
        weekly[day.strftime('%a')] = round(sum(daily)/len(daily), 1) if daily else 0

    return jsonify({
        "moodDistribution": dist,
        "weeklyTrends": weekly
    })

@app.route('/api/clear-mood', methods=['POST'])
def clear_mood_entries():
    global mood_entries
    mood_entries = []
    return jsonify({"status": "success", "message": "All mood entries cleared."})

@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    global mood_entries
    mood_entries = []
    return jsonify({"status": "success", "message": "Account and data deleted."})

# ✅ Render-compatible run block
if __name__ == '__main__':
    print("✅ Flask app is running...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
