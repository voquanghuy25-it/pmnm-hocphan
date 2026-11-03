
from flask import Flask, render_template, request
app = Flask(__name__)

#Kiểm tra điểm dùng chung cho cả 3 ô
def kiem_tra_diem(diem):
  try: 
    diem = float(diem)
    if diem < 0 or diem > 10: 
      diem = "Điểm nằm trong khoảng từ 0 đến 10!"
    else: 
      return True, diem
  except ValueError:
    return False, "Vui lòng nhập một số hợp lẹ!"
  
  
@app.route("/", methods=["GET", "POST"])
def tinh_diem():
    values = {
        "cc": "",
        "gk": "",
        "ck": ""
    }

    errors = {}
    diem_hp = None
    xep_loai = None

    if request.method == "POST":
        # Lấy dữ liệu từ biểu mẫu
        values["cc"] = request.form.get("cc", "").strip()
        values["gk"] = request.form.get("gk", "").strip()
        values["ck"] = request.form.get("ck", "").strip()

        diem = {}

        # Kiểm tra cả 3 điểm bằng cùng một hàm
        for ten in ["cc", "gk", "ck"]:
            if not values[ten]:
                errors[ten] = "Vui lòng nhập điểm."
            else:
                hop_le, ket_qua = kiem_tra_diem(values[ten])

                if hop_le:
                    diem[ten] = ket_qua
                else:
                    errors[ten] = ket_qua

        # Tính điểm khi tất cả dữ liệu hợp lệ
        if not errors:
            diem_thuc = (
                diem["cc"] * 0.1
                + diem["gk"] * 0.3
                + diem["ck"] * 0.6
            )

            # Làm tròn đến 1 chữ số thập phân
            diem_hp = round(diem_thuc + 1e-9, 1)

            # Xếp loại, ưu tiên điều kiện điểm cuối kỳ
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


if __name__ == "__main__":
    app.run(debug=True)