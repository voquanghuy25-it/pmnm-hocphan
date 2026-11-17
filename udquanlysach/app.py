from typing import List, Optional

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = \
  "sqlite:///quanlysach.db"
db.init_app(app)

TEXT = {"Content-Type": "text/plain; charset=utf-8"}


# ----------------------------------------------------------------------
# 1. MODEL
# ----------------------------------------------------------------------
class Category(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100), unique=True)
  description: Mapped[Optional[str]] = mapped_column(String(255))
  # 1 danh mục có nhiều sách
  books: Mapped[List["Book"]] = relationship(back_populates="category")

  def __repr__(self):
    return f"<Category {self.id} {self.name}>"


class Book(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[str] = mapped_column(String(200))
  author: Mapped[Optional[str]] = mapped_column(String(150))
  price: Mapped[float] = mapped_column(default=0.0)
  quantity: Mapped[int] = mapped_column(default=0)
  category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
  category: Mapped["Category"] = relationship(back_populates="books")

  def __repr__(self):
    return f"<Book {self.id} {self.title}>"


with app.app_context():
  db.create_all()


def get_categories():
  return db.session.execute(
    db.select(Category).order_by(Category.name)
  ).scalars().all()


@app.context_processor
def inject_menu():
  return {"menu_categories": get_categories()}
# ----------------------------------------------------------------------
# 2. DỮ LIỆU MẪU
# ----------------------------------------------------------------------
@app.get("/them-mau")
def add_sample():
  total = db.session.scalar(db.select(func.count(Category.id)))
  if total > 0:
    return f"Đã có {total} danh mục, không thêm nữa.", TEXT

  tin = Category(name="Tin học", description="Sách lập trình, CNTT")
  before = tin.id  # chưa ghi xuống CSDL
  db.session.add(tin)  # đưa vào "giỏ" chờ ghi

  van = Category(name="Văn học", description="Tiểu thuyết, truyện ngắn")
  kinh = Category(name="Kinh tế", description="Quản trị, tài chính")
  db.session.add_all([van, kinh])

  # Gán category=<đối tượng> thì SQLAlchemy tự điền category_id khi commit
  db.session.add_all([
    Book(title="Lập trình Python", author="Nguyễn Văn A",
         price=150000, quantity=10, category=tin),
    Book(title="Cấu trúc dữ liệu", author="Trần Văn B",
         price=120000, quantity=5, category=tin),
    Book(title="Số đỏ", author="Vũ Trọng Phụng",
         price=80000, quantity=20, category=van),
    Book(title="Truyện Kiều", author="Nguyễn Du",
         price=60000, quantity=15, category=van),
    Book(title="Cha giàu cha nghèo", author="Robert Kiyosaki",
         price=110000, quantity=8, category=kinh),
  ])

  db.session.commit()  # ghi thật sự

  return (
    f"Đã thêm 3 danh mục và 5 cuốn sách. id của Tin học: "
    f"trước commit = {before}, "
    f"sau commit = {tin.id}"
  ), TEXT


# ----------------------------------------------------------------------
# 3. THỬ TRUY VẤN
# ----------------------------------------------------------------------
@app.get("/thu-truy-van")
def try_queries():
  if db.session.scalar(db.select(func.count(Category.id))) == 0:
    return "Chưa có dữ liệu, hãy mở /them-mau trước.", TEXT

  lines = []
  lines.append(f"1. get(1): {db.session.get(Category, 1)}")
  lines.append(f"2. get(99): {db.session.get(Category, 99)}")

  books = db.session.execute(db.select(Book)).scalars().all()
  lines.append(f"3. Tất cả: {len(books)} cuốn sách")

  stmt = (db.select(Book)
          .where(Book.price >= 100000)
          .order_by(Book.price.desc()))
  dat = db.session.execute(stmt).scalars().all()
  lines.append(f"4. Giá >= 100000: {dat}")

  so_do = db.session.scalar(
    db.select(Book).filter_by(title="Số đỏ"))
  lines.append(f"5. Tìm 'Số đỏ': {so_do}")

  count = db.session.scalar(db.select(func.count(Book.id)))
  avg = db.session.scalar(db.select(func.avg(Book.price)))
  tong = db.session.scalar(db.select(func.sum(Book.quantity)))
  lines.append(f"6. Số sách: {count}, giá TB: {avg:.0f}, tổng SL: {tong}")

  # JOIN: sách thuộc danh mục "Tin học"
  stmt = (db.select(Book)
          .join(Category)
          .where(Category.name == "Tin học"))
  tin_hoc = db.session.execute(stmt).scalars().all()
  lines.append(f"7. Sách Tin học (JOIN): {tin_hoc}")

  # Đi qua relationship: không cần viết JOIN
  tin = db.session.get(Category, 1)
  lines.append(f"8. {tin.name}.books = {tin.books}")
  lines.append(f"9. Sách đầu tiên thuộc: {books[0].category}")

  # GROUP BY: đếm số sách mỗi danh mục
  rows = db.session.execute(
    db.select(Category.name, func.count(Book.id))
    .select_from(Category).outerjoin(Book)
    .group_by(Category.id)
  ).all()
  lines.append(f"10. Số sách theo danh mục: {rows}")

  return "\n".join(lines), TEXT


# ----------------------------------------------------------------------
# 4. DASHBOARD
# ----------------------------------------------------------------------
@app.get("/")
def dashboard():
  total_categories = db.session.scalar(db.select(func.count(Category.id)))
  total_books = db.session.scalar(db.select(func.count(Book.id)))
  total_quantity = db.session.scalar(
    db.select(func.coalesce(func.sum(Book.quantity), 0)))
  total_value = db.session.scalar(
    db.select(func.coalesce(func.sum(Book.price * Book.quantity), 0)))

  stats = db.session.execute(
    db.select(Category.id, Category.name, func.count(Book.id))
    .select_from(Category).outerjoin(Book)
    .group_by(Category.id).order_by(Category.name)
  ).all()

  latest_books = db.session.execute(
    db.select(Book).order_by(Book.id.desc()).limit(5)
  ).scalars().all()

  return render_template(
    "dashboard.html",
    total_categories=total_categories,
    total_books=total_books,
    total_quantity=total_quantity,
    total_value=total_value,
    stats=stats,
    latest_books=latest_books,
  )


# ----------------------------------------------------------------------
# 5. CRUD DANH MỤC
# ----------------------------------------------------------------------
@app.get("/danh-muc")
def category_list():
  return render_template("category_list.html", categories=get_categories())


@app.route("/danh-muc/them", methods=["GET", "POST"])
def category_add():
  if request.method == "POST":
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip() or None
    if not name:
      flash("Tên danh mục không được để trống.", "error")
    elif db.session.scalar(db.select(Category).filter_by(name=name)):
      flash("Tên danh mục đã tồn tại.", "error")
    else:
      db.session.add(Category(name=name, description=description))
      db.session.commit()
      flash("Đã thêm danh mục.", "success")
      return redirect(url_for("category_list"))
  return render_template("category_form.html", category=None)


@app.route("/danh-muc/<int:category_id>/sua", methods=["GET", "POST"])
def category_edit(category_id):
  category = db.get_or_404(Category, category_id)
  if request.method == "POST":
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip() or None
    trung = db.session.scalar(
      db.select(Category).where(Category.name == name,
                                Category.id != category_id))
    if not name:
      flash("Tên danh mục không được để trống.", "error")
    elif trung:
      flash("Tên danh mục đã tồn tại.", "error")
    else:
      category.name = name
      category.description = description
      db.session.commit()
      flash("Đã cập nhật danh mục.", "success")
      return redirect(url_for("category_list"))
  return render_template("category_form.html", category=category)


@app.post("/danh-muc/<int:category_id>/xoa")
def category_delete(category_id):
  category = db.get_or_404(Category, category_id)
  if category.books:
    flash("Không thể xóa: danh mục này còn sách.", "error")
  else:
    db.session.delete(category)
    db.session.commit()
    flash("Đã xóa danh mục.", "success")
  return redirect(url_for("category_list"))


# ----------------------------------------------------------------------
# 6. CRUD SÁCH THEO DANH MỤC
# ----------------------------------------------------------------------
@app.get("/danh-muc/<int:category_id>/sach")
def book_list(category_id):
  category = db.get_or_404(Category, category_id)
  books = db.session.execute(
    db.select(Book).where(Book.category_id == category_id)
    .order_by(Book.title)
  ).scalars().all()
  return render_template("book_list.html", category=category, books=books)


def read_book_form():
  """Đọc + kiểm tra form sách. Trả về (dữ liệu, lỗi)."""
  title = request.form.get("title", "").strip()
  author = request.form.get("author", "").strip() or None
  try:
    price = float(request.form.get("price", "0") or 0)
    quantity = int(request.form.get("quantity", "0") or 0)
    category_id = int(request.form.get("category_id"))
  except (TypeError, ValueError):
    return None, "Giá, số lượng hoặc danh mục không hợp lệ."
  if not title:
    return None, "Tên sách không được để trống."
  if price < 0 or quantity < 0:
    return None, "Giá và số lượng không được âm."
  if db.session.get(Category, category_id) is None:
    return None, "Danh mục không tồn tại."
  return dict(title=title, author=author, price=price,
              quantity=quantity, category_id=category_id), None


@app.route("/danh-muc/<int:category_id>/sach/them", methods=["GET", "POST"])
def book_add(category_id):
  category = db.get_or_404(Category, category_id)
  if request.method == "POST":
    data, error = read_book_form()
    if error:
      flash(error, "error")
    else:
      db.session.add(Book(**data))
      db.session.commit()
      flash("Đã thêm sách.", "success")
      return redirect(url_for("book_list", category_id=data["category_id"]))
  return render_template("book_form.html", book=None, category=category,
                         categories=get_categories())


@app.route("/sach/<int:book_id>/sua", methods=["GET", "POST"])
def book_edit(book_id):
  book = db.get_or_404(Book, book_id)
  if request.method == "POST":
    data, error = read_book_form()
    if error:
      flash(error, "error")
    else:
      for key, value in data.items():
        setattr(book, key, value)
      db.session.commit()
      flash("Đã cập nhật sách.", "success")
      return redirect(url_for("book_list", category_id=book.category_id))
  return render_template("book_form.html", book=book, category=book.category,
                         categories=get_categories())


@app.post("/sach/<int:book_id>/xoa")
def book_delete(book_id):
  book = db.get_or_404(Book, book_id)
  category_id = book.category_id
  db.session.delete(book)
  db.session.commit()
  flash("Đã xóa sách.", "success")
  return redirect(url_for("book_list", category_id=category_id))


if __name__ == "__main__":
  app.run(debug=True)