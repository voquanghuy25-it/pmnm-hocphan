from flask import Flask, url_for, request, abort, redirect, make_response
from markupsafe import escape  # Sử dụng escape để chống lỗ hổng XSS

app = Flask(__name__)

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "Lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.07}},
    "23T1020002": {"name": "Trần Thị Bình", "Lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "Lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.07}},
    "23T1020004": {"name": "Phạm Văn Dũng", "Lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "Lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "Lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.03}},
}


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


def link(endpoint, nhan, **kw):
    return f'<a href="{url_for(endpoint, **kw)}">{nhan}</a>'


def thanh_lien_ket():
    return (
        link("index", "Trang chủ") + " | "
        + link("student_list", "Danh sách sinh viên (/students)") + " | "
        + link("api_students", "API sinh viên (/api/students)") + " | "
        + link("search", "Tìm kiếm (/search)")
    )


def lay_sv(mssv):
    sv = STUDENTS.get(mssv)
    if sv is None:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return sv


# ---------- Câu 1 ----------
@app.route("/")
def index():
    tong_sv = len(STUDENTS)
    so_lop = len({sv["Lop"] for sv in STUDENTS.values()})
    return f"""
    {thanh_lien_ket()}
    <hr>
    <h1>Trang chủ - Quản lý sinh viên</h1>
    <ul>
        <li><b>Tổng số sinh viên:</b> {tong_sv}</li>
        <li><b>Số lớp (không trùng):</b> {so_lop}</li>
    </ul>
    """


# ---------- Câu 2 ----------
@app.route("/students")
def student_list():
    lop = request.args.get("lop", "").strip()

    ds_lop = sorted({sv["Lop"] for sv in STUDENTS.values()})
    thanh_loc = [link("student_list", "Tất cả")]
    for l in ds_lop:
        thanh_loc.append(link("student_list", l, lop=l))

    ket_qua = {
        mssv: sv for mssv, sv in STUDENTS.items()
        if not lop or sv["Lop"].lower() == lop.lower()
    }

    body = [
        thanh_lien_ket(),
        "<hr>",
        "<h1>Danh sách sinh viên</h1>",
        "<p><b>Lọc theo lớp:</b> " + " | ".join(thanh_loc) + "</p>",
    ]

    if not ket_qua:
        body.append("<p><i>Không có sinh viên phù hợp.</i></p>")
        return "".join(body)

    table_rows = []
    for mssv, sv in ket_qua.items():
        dtb = diem_tb(sv)
        dtb_text = f"{dtb:.2f}" if dtb is not None else "–"
        table_rows.append(
            f"<tr>"
            f"<td>{link('student_detail', mssv, mssv=mssv)}</td>"
            f"<td>{sv['name']}</td>"
            f"<td>{sv['Lop']}</td>"
            f"<td>{dtb_text}</td>"
            f"<td>{xep_loai(dtb)}</td>"
            f"</tr>"
        )

    table_html = f"""
    <table border="1" cellpadding="6" cellspacing="0">
        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        </thead>
        <tbody>
            {''.join(table_rows)}
        </tbody>
    </table>
    """
    body.append(table_html)
    return "".join(body)


# ---------- Câu 3: Chi tiết sinh viên ----------
@app.route("/students/<mssv>")
def student_detail(mssv):
    sv = lay_sv(mssv)
    dtb = diem_tb(sv)
    dtb_text = f"{dtb:.2f}" if dtb is not None else "–"

    if sv["scores"]:
        score_rows = [
            f"<tr><td>{hp}</td><td>{diem}</td></tr>"
            for hp, diem in sv["scores"].items()
        ]
        score_table = f"""
        <table border="1" cellpadding="6" cellspacing="0">
            <thead>
                <tr>
                    <th>Học phần</th>
                    <th>Điểm</th>
                </tr>
            </thead>
            <tbody>
                {''.join(score_rows)}
            </tbody>
        </table>
        """
    else:
        score_table = "<p><i>Chưa có điểm.</i></p>"

    short_url = url_for("short_link", mssv=mssv)

    return f"""
    {thanh_lien_ket()}
    <hr>
    <h1>Chi tiết sinh viên</h1>
    <ul>
        <li><b>Họ tên:</b> {sv['name']}</li>
        <li><b>MSSV:</b> {mssv}</li>
        <li><b>Lớp:</b> {link('student_list', sv['Lop'], lop=sv['Lop'])}</li>
        <li><b>Điểm TB:</b> {dtb_text}</li>
        <li><b>Xếp loại:</b> {xep_loai(dtb)}</li>
    </ul>

    <h3>Bảng điểm:</h3>
    {score_table}

    <br>
    <p>
        {link("export_scores", "Tải bảng điểm (CSV)", mssv=mssv)} | 
        Link rút gọn: {link("short_link", short_url, mssv=mssv)}
    </p>
    <p>{link("student_list", "← Quay lại danh sách sinh viên")}</p>
    """


# ---------- Câu 4: Link rút gọn, chuyển hướng 301 ----------
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


# ---------- Câu 6: Tìm kiếm an toàn (Sửa lỗi XSS) ----------
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()

    # Chống lỗ hổng XSS bằng hàm escape() cho cả 2 trường hợp kiểm tra:
    # 1. /search?q=<script>alert(1)</script>
    # 2. /search?q="><script>alert(1)</script>
    q_safe = escape(q) if q else ""

    ket_qua = []
    if q:
        tu_khoa = q.lower()
        for mssv, sv in STUDENTS.items():
            if tu_khoa in sv["name"].lower() or tu_khoa in mssv.lower():
                ket_qua.append({"mssv": mssv, "name": sv["name"], "lop": sv["Lop"]})

    body = [
        thanh_lien_ket(),
        "<hr>",
        "<h1>Tìm kiếm sinh viên</h1>",
        f'<form method="get" action="{url_for("search")}">',
        f'  <input type="text" name="q" value="{q_safe}" placeholder="Họ tên hoặc MSSV">',
        '  <button type="submit">Tìm</button>',
        '</form>',
    ]

    if q:
        body.append(f'<p>Tìm thấy {len(ket_qua)} kết quả cho "{q_safe}"</p>')
        if ket_qua:
            body.append("<ul>")
            for r in ket_qua:
                link_detail = url_for("student_detail", mssv=r["mssv"])
                body.append(
                    f'<li><a href="{link_detail}">{r["mssv"]}</a> - {r["name"]} - {r["lop"]}</li>'
                )
            body.append("</ul>")

    return "".join(body)


@app.route("/api/students")
def api_students():
    return STUDENTS


if __name__ == "__main__":
    app.run(debug=False)
