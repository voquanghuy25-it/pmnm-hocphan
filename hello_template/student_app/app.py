
from flask import Flask, render_template, url_for, request, abort, redirect, make_response
from datetime import datetime
app = Flask(__name__)
# Hiển thị tiếng Việt có dấu chuẩn khi xuất JSON
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "Lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.07}},
    "23T1020002": {"name": "Trần Thị Bình", "Lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "Lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.07}},
    "23T1020004": {"name": "Phạm Văn Dũng", "Lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "Lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "Lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.03}},
}


# --- HÀM PHỤ TRỢ (LOGIC) ---
def diem_tb(sv):
    scores = sv["scores"]
    if not scores:
        return None
    return sum(scores.values()) / len(scores)


def xep_loai(dtb):
    if dtb is None:
        return "–"
    if dtb >= 8:
        return "Giỏi"
    if dtb >= 6.5:
        return "Khá"
    if dtb >= 5:
        return "Trung bình"
    return "Yếu"


def lay_sv(mssv):
    sv = STUDENTS.get(mssv)
    if sv is None:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return sv


# ---------- Câu 1: Trang chủ ----------
@app.route("/")
def index():
    tong_sv = len(STUDENTS)
    so_lop = len({sv["Lop"] for sv in STUDENTS.values()})
    return render_template("index.html", tong_sv=tong_sv, so_lop=so_lop)


# ---------- Câu 2: Danh sách sinh viên ----------
@app.route("/students")
def student_list():
    lop = request.args.get("lop", "").strip()
    ds_lop = sorted({sv["Lop"] for sv in STUDENTS.values()})

    danh_sach = []
    for mssv, sv in STUDENTS.items():
        if not lop or sv["Lop"].lower() == lop.lower():
            dtb = diem_tb(sv)
            danh_sach.append({
                "mssv": mssv,
                "name": sv["name"],
                "lop": sv["Lop"],
                "dtb_text": f"{dtb:.2f}" if dtb is not None else "–",
                "xep_loai": xep_loai(dtb)
            })

    return render_template(
        "student_list.html",
        danh_sach=danh_sach,
        ds_lop=ds_lop,
        current_lop=lop
    )


# ---------- Câu 3: Chi tiết sinh viên ----------
@app.route("/students/<mssv>")
def student_detail(mssv):
    sv = lay_sv(mssv)
    dtb = diem_tb(sv)
    dtb_text = f"{dtb:.2f}" if dtb is not None else "–"

    return render_template(
        "student_detail.html",
        mssv=mssv,
        sv=sv,
        dtb_text=dtb_text,
        xep_loai=xep_loai(dtb)
    )


# ---------- Câu 4: Link rút gọn (301) ----------
@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


# ---------- Câu 5: Xuất CSV ----------
@app.route("/students/<mssv>/export")
def export_scores(mssv):
    sv = lay_sv(mssv)
    dong = ["hoc_phan,diem"]
    for hp, diem in sv["scores"].items():
        dong.append(f"{hp},{diem}")
    noi_dung = "\n".join(dong) + "\n"

    resp = make_response(noi_dung)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return resp


# ---------- Câu 6: Tìm kiếm ----------
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    ket_qua = []
    if q:
        tu_khoa = q.lower()
        for mssv, sv in STUDENTS.items():
            if tu_khoa in sv["name"].lower() or tu_khoa in mssv.lower():
                ket_qua.append({"mssv": mssv, "name": sv["name"], "lop": sv["Lop"]})

    return render_template("search.html", q=q, ket_qua=ket_qua)


# ---------- API ----------
@app.route("/api/students")
def api_students():
    return STUDENTS


# ---------- Xử lý lỗi 404 ----------
@app.errorhandler(404)
def page_not_found(error):
    desc = error.description if hasattr(error, 'description') else "Trang không tồn tại."
    return render_template("404.html", description=desc), 404

# ---------- Thêm trang Giới thiệu (About) ----------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------- Trang Liên hệ (Contact) ----------
@app.route("/contact")
def contact():
    return render_template("contact.html")
  
  # Context Processor: Tự động gửi các biến/hàm này vào MỌI template
@app.context_processor
def inject_globals():
    # Hàm tiện ích kiểm tra xem route hiện tại có trùng với endpoint hay không
    def is_active(endpoint):
        return "text-danger fw-bold active" if request.endpoint == endpoint else ""
    
    return {
        "site_name": "QL Sinh Viên",
        "current_year": datetime.now().year,  # Tự động lấy năm hiện tại
        "is_active": is_active                # Trả về hàm is_active để dùng trong HTML
    }
if __name__ == "__main__":
    app.run(debug=True, port=8000)