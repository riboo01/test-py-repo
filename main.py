from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import requests
import re
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
        return redirect(url_for('dashboard'))  # Redirect to dashboard
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

@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_input = request.json.get("message")
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "HTTP-Referer": "http://localhost:5001",
        "X-Title": "MindMate",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly and caring mental health support assistant named MindMate. "
                    "Keep your answers short and supportive — like a friend who listens and gently helps. "
                    "Avoid formal language or long lists. Use a warm and kind tone, maybe include an emoji if it feels natural. "
                    "Don’t overexplain unless asked. Focus on empathy and emotional connection."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        response = requests.post(openrouter_url, headers=headers, json=payload)
        data = response.json()
        reply = data['choices'][0]['message']['content']
        clean_reply = re.sub(r"[#*`>_~]", "", reply)
        return jsonify({"reply": clean_reply})
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"reply": "Sorry, I couldn't process that right now."}), 500

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
    # Distribution
    dist = collections.Counter(e['mood'] for e in mood_entries)

    # Weekly Trends
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


if __name__ == '__main__':
    print("✅ Flask app is running...")

    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

