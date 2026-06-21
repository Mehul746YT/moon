import os
import requests
import resend
from flask import Flask, request, jsonify, redirect, session

# Initialize App
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-this-to-a-random-string")

# API Configuration
resend.api_key = os.environ.get("re_6nVv882w_LS24pN1wVMTQT9MtntZJKMPQ")
DISCORD_CLIENT_ID = os.environ.get("1518239264108843048")
DISCORD_CLIENT_SECRET = os.environ.get("J8u8QN29F-QDAskJmOYAlALx9ysMQW7x")
REDIRECT_URI = os.environ.get("https://moon-1pojt6nqj-mehul-sharmas-projects-fa35c4d3.vercel.app") # e.g., https://your-app.vercel.app/api/callback

# --- AUTH ROUTES ---

@app.route('/api/auth/discord')
def discord_login():
    return redirect(f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")
print(f"DEBUG: Redirecting to {auth_url}") 
    return redirect(auth_url)

@app.route('/api/callback')
def callback():
    code = request.args.get('code')
    # Exchange code for token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    token_resp = requests.post("https://discord.com/api/oauth2/token", data=data).json()
    
    # Fetch user info
    headers = {"Authorization": f"Bearer {token_resp['access_token']}"}
    user_info = requests.get("https://discord.com/api/users/@me", headers=headers).json()
    
    session['user'] = user_info['username']
    return redirect('/?authenticated=true')

# --- QUIZ LOGIC ---

def calculate_score(answers):
    # Basic server-side grading logic
    correct_answers = {'q1': '21m', 'q2': 'satoshi'}
    score = 0
    for q, ans in answers.items():
        if correct_answers.get(q) == ans:
            score += 50
    return score

@app.route('/api/submit', methods=['POST'])
def submit():
    # Ensure user is authenticated via Discord
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_id = session.get('user')
    answers = data.get('answers', {})
    contact_info = data.get('contact_info')
    
    # Grade the quiz
    score = calculate_score(answers)
    
    # Send results via Email API
    try:
        email_content = f"""
        <h1>New Quiz Submission</h1>
        <p><b>User:</b> {user_id}</p>
        <p><b>Score:</b> {score}/100</p>
        <p><b>Contact Info (LN/Discord):</b> {contact_info}</p>
        """
        
        resend.Emails.send({
            "from": "Quiz App <onboarding@resend.dev>",
            "to": ["mehul.sharma746c@gmail.com"],
            "subject": f"New Quiz Result: {user_id}",
            "html": email_content
        })
        
        return jsonify({"status": "success", "message": "Results sent to admin!"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
