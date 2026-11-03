from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo, ValidationError

app = Flask(__name__)
app.secret_key = "chi-dung-khi-hoc"
app.permanent_session_lifetime = timedelta(days=7)

# Thống nhất cấu trúc lưu trữ USERS dưới dạng Dict
USERS = {
    "admin": {"email": "admin@gmail.com", "password": "admin123"},
    "an": {"email": "an@gmail.com", "password": "an123456"}
}



# ---------------------------------------------------------
# BÀI 1: MÁY TÍNH
# ---------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def calculator():
    values = {"a": "", "op": "+", "b": ""}
    errors = {}
    result = None

    if request.method == "POST":
        values["a"] = request.form.get("a", "").strip()
        values["op"] = request.form.get("op", "+")
        values["b"] = request.form.get("b", "").strip()

        a = None
        b = None

        if not values["a"]:
            errors["a"] = "Vui lòng nhập số a."
        else:
            try:
                a = float(values["a"])
            except ValueError:
                errors["a"] = "Vui lòng nhập một số hợp lệ."

        if not values["b"]:
            errors["b"] = "Vui lòng nhập số b."
        else:
            try:
                b = float(values["b"])
            except ValueError:
                errors["b"] = "Vui lòng nhập một số hợp lệ."

        if values["op"] not in ["+", "-", "*", "/"]:
            errors["op"] = "Phép tính không hợp lệ."

        if not errors:
            if values["op"] == "+":
                result = a + b
            elif values["op"] == "-":
                result = a - b
            elif values["op"] == "*":
                result = a * b
            elif values["op"] == "/":
                if b == 0:
                    errors["b"] = "Không thể chia cho 0."
                else:
                    result = a / b

    return render_template(
        "calc.html",
        values=values,
        errors=errors,
        result=result
    )


# ---------------------------------------------------------
# BÀI 2: TÍNH ĐIỂM HỌC PHẦN
# ---------------------------------------------------------
def kiem_tra_diem(diem):
    try:
        diem = float(diem)
        if diem < 0 or diem > 10:
            return False, "Điểm nằm trong khoảng từ 0 đến 10!"
        else:
            return True, diem
    except ValueError:
        return False, "Vui lòng nhập một số hợp lệ!"


@app.route("/tinhdiem", methods=["GET", "POST"])
def tinh_diem():
    values = {"cc": "", "gk": "", "ck": ""}
    errors = {}
    diem_hp = None
    xep_loai = None

    if request.method == "POST":
        values["cc"] = request.form.get("cc", "").strip()
        values["gk"] = request.form.get("gk", "").strip()
        values["ck"] = request.form.get("ck", "").strip()

        diem = {}

        for ten in ["cc", "gk", "ck"]:
            if not values[ten]:
                errors[ten] = "Vui lòng nhập điểm."
            else:
                hop_le, ket_qua = kiem_tra_diem(values[ten])
                if hop_le:
                    diem[ten] = ket_qua
                else:
                    errors[ten] = ket_qua

        if not errors:
            diem_thuc = (
                diem["cc"] * 0.1
                + diem["gk"] * 0.3
                + diem["ck"] * 0.6
            )
            diem_hp = round(diem_thuc + 1e-9, 1)

            if diem["ck"] < 4:
                xep_loai = "F"
            elif diem_hp >= 8.5:
                xep_loai = "A"
            elif diem_hp >= 7.0:
                xep_loai = "B"
            elif diem_hp >= 5.5:
                xep_loai = "C"
            elif diem_hp >= 4.0:
                xep_loai = "D"
            else:
                xep_loai = "F"

    return render_template(
        "index.html",
        values=values,
        errors=errors,
        diem_hp=diem_hp,
        xep_loai=xep_loai
    )


# ---------------------------------------------------------
# BÀI 3: TÍNH CHỈ SỐ BMI
# ---------------------------------------------------------
def kiem_tra_cao(cao_str):
    if not cao_str:
        return False, "Vui lòng nhập chiều cao."
    try:
        val = float(cao_str.replace(",", "."))
        if val <= 2.5:
            return False, "Giá trị phải từ 50 đến 250 (nhập mét thay vì cm)."
        if val < 50 or val > 250:
            return False, "Lỗi ô chiều cao: Giá trị phải từ 50 đến 250."
        return True, val
    except ValueError:
        return False, "Lỗi ô chiều cao: Vui lòng nhập một số."


def kiem_tra_nang(nang_str):
    if not nang_str:
        return False, "Vui lòng nhập cân nặng."
    try:
        val = float(nang_str.replace(",", "."))
        if val < 10 or val > 300:
            return False, "Lỗi ô cân nặng: Giá trị phải từ 10 đến 300."
        return True, val
    except ValueError:
        return False, "Lỗi ô cân nặng: Vui lòng nhập một số."


@app.route("/bmi", methods=["GET", "POST"])
def tinh_bmi():
    values = {"cao": "", "nang": ""}
    errors = {}
    bmi = None
    phan_loai = None
    mau_sac = None
    can_nang_nen_co = None

    if request.method == "POST":
        values["cao"] = request.form.get("cao", "").strip()
        values["nang"] = request.form.get("nang", "").strip()

        cao_val = None
        nang_val = None

        hop_le_cao, ket_qua_cao = kiem_tra_cao(values["cao"])
        if hop_le_cao:
            cao_val = ket_qua_cao
        else:
            errors["cao"] = ket_qua_cao

        hop_le_nang, ket_qua_nang = kiem_tra_nang(values["nang"])
        if hop_le_nang:
            nang_val = ket_qua_nang
        else:
            errors["nang"] = ket_qua_nang

        if not errors:
            h_m = cao_val / 100.0
            bmi_thuc = nang_val / (h_m ** 2)
            bmi = round(bmi_thuc + 1e-9, 1)

            if bmi < 18.5:
                phan_loai = "Thiếu cân"
                mau_sac = "warning"
            elif bmi < 23.0:
                phan_loai = "Bình thường"
                mau_sac = "success"
            elif bmi < 25.0:
                phan_loai = "Thừa cân"
                mau_sac = "warning"
            else:
                phan_loai = "Béo phì"
                mau_sac = "danger"

            w_min = round(18.5 * (h_m ** 2) + 1e-9, 1)
            w_max = round(22.9 * (h_m ** 2) + 1e-9, 1)
            can_nang_nen_co = f"{w_min} – {w_max} kg"

    return render_template(
        "bmi.html",
        values=values,
        errors=errors,
        bmi=bmi,
        phan_loai=phan_loai,
        mau_sac=mau_sac,
        can_nang_nen_co=can_nang_nen_co
    )


# ---------------------------------------------------------
# BÀI 4: ĐĂNG NHẬP / ĐĂNG XUẤT / PROFILE
# ---------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")
    name = ""
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        # Kiểm tra tài khoản dạng dict hoặc string
        if name in USERS:
            user_data = USERS[name]
            saved_password = user_data["password"] if isinstance(user_data, dict) else user_data

            if saved_password == password:
                session["user"] = name
                session.permanent = remember
                flash(f"Đăng nhập thành công. Xin chào {name}!", "success")
                return redirect("/")

        flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")

    return render_template("login.html", username=name)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    flash("Bạn đã đăng xuất!", "info")
    return redirect("/")


@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Vui lòng đăng nhập để xem trang này.", "warning")
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["user"])

# ---------------------------------------------------------
# FORM ĐĂNG KÝ TÀI KHOẢN (FLASK-WTF)
# ---------------------------------------------------------
class RegisterForm(FlaskForm):
    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập."),
            Length(min=4, max=20, message="Độ dài từ 4 đến 20 ký tự."),
            Regexp(r'^[a-z0-9_]+$', message="Chỉ dùng chữ thường không dấu, số và _.")
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Email không đúng định dạng.")
        ]
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu."),
            Length(min=8, message="Mật khẩu tối thiểu 8 ký tự.")
        ]
    )
    confirm_password = PasswordField(
        "Nhập lại mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập lại mật khẩu."),
            EqualTo("password", message="Mật khẩu nhập lại không khớp.")
        ]
    )
    tos = BooleanField(
        "Tôi đồng ý với các điều khoản",
        validators=[
            DataRequired(message="Bạn phải đồng ý với điều khoản.")
        ]
    )
    submit = SubmitField("Đăng ký")

    # Kiểm tra trùng tên đăng nhập trong USERS
    def validate_username(self, field):
        if field.data in USERS:
            raise ValidationError("Tên đăng nhập đã được sử dụng.")


# Route Đăng ký (chỉ giữ 1 route duy nhất)
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Thêm tài khoản mới vào USERS
        USERS[form.username.data] = {
            "email": form.email.data,
            "password": form.password.data
        }
        flash("Đăng ký thành công.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)