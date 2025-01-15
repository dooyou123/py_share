import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from supabase import create_client, Client
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv  # dotenv 추가
from forms import LoginForm
from models import User

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_mapping(
    SUPABASE_URL="https://uoyknxfdxixodakuhapz.supabase.co",  # 실제 Supabase URL
    SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVveWtueGZkeGl4b2Rha3VoYXB6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY5NjU3OTMsImV4cCI6MjA1MjU0MTc5M30.asqdLrx__j00oZ3iylxEgB_zIceAGP7BPnqQpkvtOwg",  # 실제 Supabase API Key
    SECRET_KEY="s0MeS3cr3T_kEy!",
)

# Supabase 클라이언트 생성
SUPABASE_URL = app.config["SUPABASE_URL"]
SUPABASE_KEY = app.config["SUPABASE_KEY"]


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# 가상의 사용자 데이터 (실제로는 데이터베이스에서 가져와야 함)
users = {  # 키를 정수형으로 수정
    1: User(1, "front", generate_password_hash("pass@0203")),
    2: User(2, "back", generate_password_hash("password2")),
}


@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = next(
            (u for u in users.values() if u.username == form.username.data), None
        )
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index"))  # redirect 수정
        else:
            flash("잘못된 사용자 이름 또는 비밀번호입니다.")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))  # 로그아웃 후 로그인 페이지로 redirect


@app.route("/")
@login_required  # 로그인이 필요한 경로에 데코레이터 추가
def index():
    return render_template(
        "index.html", username=current_user.username
    )  # 템플릿에 사용자 이름 전달


@app.route("/add_entry", methods=["POST"])
def add_entry():
    try:
        data = request.get_json()
        name = data["name"]
        date = data["date"]
        shift = data["shift"]
        notes = data["notes"]
        created = data["created"]

        # Supabase 테이블에 데이터 삽입
        response = (
            supabase.table("share")
            .insert(
                {
                    "name": name,
                    "date": date,
                    "shift": shift,
                    "notes": notes,
                    "created": created,
                }
            )
            .execute()
        )

        # 응답 처리
        if response.data:
            return jsonify({"message": "Entry added successfully!"}), 201
        elif response.error:  # Supabase에서 발생한 에러 처리
            raise ValueError(f"Supabase error: {response.error.message}")
        else:
            return jsonify({"message": "Unknown error occurred!"}), 500

    except Exception as e:
        app.logger.error(f"Error in add_entry: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/get_entries", methods=["GET"])
def get_entries():
    try:
        # Supabase 데이터 조회
        response = supabase.table("share").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete_entry", methods=["POST"])
def delete_entry():
    try:
        data = request.get_json()
        entry_id = data["id"]

        # Supabase에서 데이터 삭제
        supabase.table("share").delete().eq("id", entry_id).execute()
        return jsonify({"message": "Entry deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
