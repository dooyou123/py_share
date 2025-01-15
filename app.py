from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)  # 비밀번호 해싱 추가
from forms import LoginForm
from models import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "s0MeS3cr3T_kEy!"

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


# Google Sheets API setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
gc = gspread.authorize(credentials)
spreadsheet = gc.open("ShiftHandover")  # Name of your Google Spreadsheet
sheet = spreadsheet.sheet1  # Access the first sheet


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

        # Add the entry to Google Sheets
        sheet.append_row([name, date, shift, notes])
        return jsonify({"message": "Entry added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# get_entries route 수정
@app.route("/get_entries", methods=["GET"])
def get_entries():
    try:
        records = sheet.get_all_records(empty2zero=False, head=1)
        # last_updated를 date로 변경
        for record in records:
            if "last_updated" in record:
                record["date"] = record.pop("last_updated")
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete_entry", methods=["POST"])
def delete_entry():
    try:
        data = request.get_json()
        row_number = data["row_number"]

        # Delete the row from Google Sheets
        sheet.delete_rows(row_number)
        return jsonify({"message": "Entry deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
