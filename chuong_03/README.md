# Chương 3 - Flask căn bản

## btap_VoQuangHuy - So Diem

Chạy:

    pip install flask
    flask --app sodiem run

### Lệnh/URL đã kiểm thử

| Chức năng | Lệnh / URL | Kết quả |
|---|---|---|
| Trang chủ | `curl http://127.0.0.1:5000/` | Hiển thị tổng số SV và số lớp |
| Danh sách | `curl http://127.0.0.1:5000/students` | Bảng danh sách sinh viên |
| Lọc theo lớp | `curl "http://127.0.0.1:5000/students?lop=K47A"` | Chỉ hiện SV lớp K47A |
| Chi tiết SV | `curl http://127.0.0.1:5000/students/23T1020001` | Thông tin và bảng điểm |
| Link rút gọn | `curl -i http://127.0.0.1:5000/sv/23T1020001` | HTTP 301, chuyển đến trang chi tiết |
| Xuất CSV | `curl -OJ http://127.0.0.1:5000/students/23T1020001/export` | Tải file `diem_23T1020001.csv` |
| SV không tồn tại | `curl -i http://127.0.0.1:5000/students/99999` | HTTP 404 |
