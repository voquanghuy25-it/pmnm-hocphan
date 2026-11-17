from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, func
from typing import List, Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "chuoi-bi-mat-bat-ky"
app.config["SQLALCHEMY_DATABASE_URI"] = \
  "sqlite:///quanlysach.db"

db.init_app(app)

@app.route("/")
def index():
  return "Xin chào, đây là ứng dụng quản lý sách!"

#Model Category
TEXT = {"Content-Type": "text/plain; charset=utf-8"}
class Category(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100), unique=True) # unique=True: không cho trùng
  
  #Optional[str] nghĩa là “chuỗi hoặc None”, tức cột được phép để trống.
  description: Mapped[Optional[str]] = mapped_column(String(255))
  
  #List["Book"]: báo đây là qhe 1-n: 1 danh mục có nhiều sách 
  # relationship(back_populates="category"): nối với thuộc tính tên category bên class Book. 
  
  books: Mapped[List["Book"]] = relationship(back_populates="category")
  def __repr__(self):
    return f"<Category {self.id} {self.name}>"


# Class Book 
class Book(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[String] = mapped_column(String(200))
  author: Mapped[Optional[String]] = mapped_column(String(150))
  price: Mapped[float] = mapped_column(default=0.0)
  quantity: Mapped[int] = mapped_column(default=0)
  Category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
  category: Mapped["Category"] = relationship(back_populates="books")
  def __repr__(self):
     return f"<Book {self.id} {self.title}"
    
# Tạo bảng 
with app.app_context():
    db.create_all()
    
def get_categories():
    return db.session.execute(
        db.select(Category).order_by(Category.name)
    ).scalars().all()
# ----------------------------------------------------------------------
# 3. DASHBOARD
# ----------------------------------------------------------------------
@app.get("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id)))
    total_books = db.session.scalar(db.select(func.count(Book.id)))
    total_quantity = db.session.scalar(
        db.select(func.coalesce(func.sum(Book.quantity), 0)))
    total_value = db.session.scalar(
        db.select(func.coalesce(func.sum(Book.price * Book.quantity), 0)))
    
    # Số đầu sách theo từng danh mục (outer join để danh mục rỗng vẫn hiện)
    stats = db.session.execute(
        db.select(Category.id, Category.name, func.count(Book.id))
        .select_from(Category)
        .outerjoin(Book)
        .group_by(Category.id)
        .order_by(Category.name)
    ).all()

    latest_books = db.session.scalars(
        db.select(Book).order_by(Book.id.desc()).limit(5)).all()
    
    return render_template(
       "dashboard.html",
        total_categories=total_categories,
        total_books=total_books,
        total_quantity=total_quantity,
        total_value=total_value,
        stats=stats,
        latest_books=latest_books,
    )


  
if __name__=="__main__":
  app.run(debug=True)