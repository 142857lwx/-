from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    student_id = db.Column(db.String(20), unique=True)
    major = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('admin', 'librarian', 'student'), default='student')
    avatar_url = db.Column(db.String(500))
    total_reading_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'student_id': self.student_id,
            'major': self.major,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'total_reading_minutes': self.total_reading_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Book(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    total_stock = db.Column(db.Integer, default=0)
    available_stock = db.Column(db.Integer, default=0)
    price = db.Column(db.DECIMAL(10, 2))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    keywords = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'category': self.category,
            'location': self.location,
            'total_stock': self.total_stock,
            'available_stock': self.available_stock,
            'price': float(self.price) if self.price else None,
            'description': self.description,
            'cover_url': self.cover_url,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BorrowRecord(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.Enum('borrowed', 'returned', 'overdue', 'renewed'), default='borrowed')
    renew_count = db.Column(db.Integer, default=0)
    fine = db.Column(db.DECIMAL(10, 2), default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', backref=db.backref('borrow_records', lazy=True))
    book = db.relationship('Book', backref=db.backref('borrow_records', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'renew_count': self.renew_count,
            'fine': float(self.fine) if self.fine else None,
            'book_title': self.book.title if self.book else None,
            'user_name': self.user.real_name if self.user else None
        }

class Course(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    course_code = db.Column(db.String(50), unique=True)
    course_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    credit = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'department': self.department,
            'credit': self.credit
        }

class UserCourse(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.BigInteger, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.Date)
    grade = db.Column(db.String(10))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

    user = db.relationship('User', backref=db.backref('user_courses', lazy=True))
    course = db.relationship('Course', backref=db.backref('user_courses', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'grade': self.grade
        }

class Recommendation(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=False)
    score = db.Column(db.DECIMAL(5, 2), default=0)
    reason = db.Column(db.Text)
    recommended_at = db.Column(db.TIMESTAMP, default=datetime.now)
    clicked = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('recommendations', lazy=True))
    book = db.relationship('Book', backref=db.backref('recommendations', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'score': float(self.score) if self.score else None,
            'reason': self.reason,
            'recommended_at': self.recommended_at.isoformat() if self.recommended_at else None,
            'clicked': self.clicked
        }

class SecondHandBook(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'))
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    condition = db.Column(db.Enum('like_new', 'good', 'fair', 'poor'), default='good')
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    status = db.Column(db.Enum('available', 'reserved', 'sold'), default='available')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', backref=db.backref('second_hand_books', lazy=True))
    book = db.relationship('Book', backref=db.backref('second_hand_books', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'seller_name': self.user.real_name if self.user else None,
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'condition': self.condition,
            'price': float(self.price) if self.price else None,
            'description': self.description,
            'cover_url': self.cover_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SecondHandTransaction(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey('second_hand_book.id'), nullable=False)
    buyer_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'completed', 'cancelled'), default='pending')
    message = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    book = db.relationship('SecondHandBook', backref=db.backref('transactions', lazy=True))
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('buyer_transactions', lazy=True))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('seller_transactions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'buyer_id': self.buyer_id,
            'buyer_name': self.buyer.real_name if self.buyer else None,
            'seller_id': self.seller_id,
            'seller_name': self.seller.real_name if self.seller else None,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'status': self.status,
            'message': self.message
        }

class ReadingRecord(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=False)
    reading_date = db.Column(db.Date, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

    user = db.relationship('User', backref=db.backref('reading_records', lazy=True))
    book = db.relationship('Book', backref=db.backref('reading_records', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'reading_date': self.reading_date.isoformat() if self.reading_date else None,
            'minutes': self.minutes
        }

class StockAlert(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=False)
    threshold = db.Column(db.Integer, default=5)
    current_stock = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('active', 'resolved'), default='active')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    book = db.relationship('Book', backref=db.backref('stock_alerts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'threshold': self.threshold,
            'current_stock': self.current_stock,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BookRequest(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    reason = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'purchased'), default='pending')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', backref=db.backref('book_requests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    type = db.Column(db.Enum('overdue', 'renew', 'recommendation', 'transaction', 'system'), default='system')
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }