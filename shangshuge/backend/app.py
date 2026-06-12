import os
import hashlib
import base64
import secrets
from io import BytesIO
from datetime import datetime, date, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)


# ==================== Models ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    student_id = db.Column(db.String(20), unique=True)
    major = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='student')
    avatar_url = db.Column(db.String(500))
    total_reading_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    second_hand_books = db.relationship('SecondHandBook', backref='user', lazy=True)
    reading_records_rel = db.relationship('ReadingRecord', backref='user', lazy=True)
    book_requests = db.relationship('BookRequest', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

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
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    total_stock = db.Column(db.Integer, default=0)
    available_stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
    recommendations = db.relationship('Recommendation', backref='book', lazy=True)
    stock_alerts = db.relationship('StockAlert', backref='book', lazy=True)

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
            'price': self.price,
            'description': self.description,
            'cover_url': self.cover_url,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='borrowed')
    renew_count = db.Column(db.Integer, default=0)
    fine = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

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
            'fine': self.fine,
            'book_title': self.book.title if self.book else None,
            'user_name': self.user.real_name if self.user else None
        }


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    score = db.Column(db.Float, default=0)
    reason = db.Column(db.Text)
    recommended_at = db.Column(db.DateTime, default=datetime.now)
    clicked = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'score': self.score,
            'reason': self.reason,
            'recommended_at': self.recommended_at.isoformat() if self.recommended_at else None,
            'clicked': self.clicked
        }


class SecondHandBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    condition = db.Column(db.String(20), default='good')
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'seller_name': self.user.real_name if self.user else None,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'condition': self.condition,
            'price': self.price,
            'description': self.description,
            'cover_url': self.cover_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SecondHandTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_transactions')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_transactions')

    def to_dict(self):
        book = SecondHandBook.query.get(self.book_id)
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': book.title if book else None,
            'buyer_id': self.buyer_id,
            'buyer_name': self.buyer.real_name if self.buyer else None,
            'seller_id': self.seller_id,
            'seller_name': self.seller.real_name if self.seller else None,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'status': self.status,
            'message': self.message
        }


class ReadingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reading_date = db.Column(db.Date, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    book = db.relationship('Book', backref='reading_records')

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
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    threshold = db.Column(db.Integer, default=5)
    current_stock = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)

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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    type = db.Column(db.String(20), default='system')
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

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


# ==================== Helper Functions ====================

def generate_qr_code(data):
    if not HAS_QRCODE:
        return ''
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    return base64.b64encode(buffered.getvalue()).decode()


def hash_password(password):
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.sha256((salt + password).encode('utf-8')).hexdigest()}"


def check_password(password, hashed):
    parts = hashed.split('$')
    if len(parts) != 2:
        return False
    salt, stored_hash = parts
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest() == stored_hash


# ==================== Routes ====================

@app.route('/')
def index():
    return jsonify({'message': 'Library Management System API is running'}), 200


# ----- Auth -----

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': '用户名不存在'}), 401

    if check_password(password, user.password):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200
    return jsonify({'message': '密码错误'}), 401


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()

    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400

    if data.get('student_id') and User.query.filter_by(student_id=data.get('student_id')).first():
        return jsonify({'message': '学号已被注册'}), 400

    user = User(
        username=username,
        password=hash_password(data.get('password', '')),
        real_name=data.get('real_name'),
        student_id=data.get('student_id'),
        major=data.get('major'),
        email=data.get('email'),
        phone=data.get('phone'),
        role='student'
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201


@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user_info():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': '用户不存在'}), 404


# ----- Books -----

@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()

    query = Book.query
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(db.or_(Book.title.like(like), Book.author.like(like)))
    if category:
        query = query.filter(Book.category == category)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'books': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({'message': '图书不存在'}), 404


@app.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403

    data = request.get_json() or {}
    try:
        book = Book(
            isbn=data.get('isbn'),
            title=data['title'],
            author=data.get('author'),
            publisher=data.get('publisher'),
            category=data.get('category'),
            location=data.get('location'),
            total_stock=int(data.get('total_stock', 0) or 0),
            available_stock=int(data.get('available_stock', 0) or 0),
            price=float(data.get('price', 0) or 0),
            description=data.get('description'),
            keywords=data.get('keywords')
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': '图书添加成功', 'book': book.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加失败: {str(e)}'}), 400


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404

    data = request.get_json() or {}
    for key, value in data.items():
        if hasattr(book, key) and value is not None:
            setattr(book, key, value)
    db.session.commit()
    return jsonify({'message': '图书更新成功', 'book': book.to_dict()}), 200


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'message': '权限不足'}), 403

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': '图书删除成功'}), 200


@app.route('/api/books/<int:book_id>/qr', methods=['GET'])
def get_book_qr(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    qr_base64 = generate_qr_code(f'BOOK:{book_id}')
    return jsonify({'book_id': book.id, 'title': book.title,
                    'qr_code': f'data:image/png;base64,{qr_base64}'}), 200


@app.route('/api/books/top', methods=['GET'])
def get_top_books():
    rows = db.session.query(
        Book.id, Book.title,
        db.func.count(BorrowRecord.id).label('borrow_count')
    ).outerjoin(BorrowRecord, Book.id == BorrowRecord.book_id) \
     .group_by(Book.id, Book.title) \
     .order_by(db.desc('borrow_count')) \
     .limit(10).all()

    result = [{'id': r[0], 'title': r[1], 'borrow_count': r[2]} for r in rows]
    return jsonify(result), 200


@app.route('/api/categories', methods=['GET'])
def get_categories():
    rows = db.session.query(Book.category).filter(Book.category.isnot(None)) \
        .distinct().all()
    return jsonify([r[0] for r in rows if r[0]]), 200


# ----- Borrowing -----

@app.route('/api/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    identity = get_jwt_identity()
    user_id = identity['id']
    data = request.get_json() or {}
    book_id = data.get('book_id')

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    if book.available_stock <= 0:
        return jsonify({'message': '库存不足'}), 400

    active = BorrowRecord.query.filter(
        BorrowRecord.user_id == user_id,
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    if active >= Config.MAX_BORROW_COUNT:
        return jsonify({'message': f'已达到最大借阅数量({Config.MAX_BORROW_COUNT})'}), 400

    today = date.today()
    record = BorrowRecord(
        user_id=user_id,
        book_id=book.id,
        borrow_date=today,
        due_date=today + timedelta(days=Config.BORROW_DAYS)
    )
    book.available_stock -= 1
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': '借阅成功', 'record': record.to_dict()}), 200


@app.route('/api/borrow/<int:record_id>/renew', methods=['POST'])
@jwt_required()
def renew_book(record_id):
    identity = get_jwt_identity()
    record = BorrowRecord.query.get(record_id)
    if not record:
        return jsonify({'message': '借阅记录不存在'}), 404
    if record.user_id != identity['id']:
        return jsonify({'message': '无权操作'}), 403
    if record.status == 'returned':
        return jsonify({'message': '图书已归还'}), 400
    if record.renew_count >= Config.MAX_RENEW_COUNT:
        return jsonify({'message': '已达到最大续借次数'}), 400

    record.due_date += timedelta(days=Config.BORROW_DAYS)
    record.renew_count += 1
    record.status = 'renewed'

    notif = Notification(
        user_id=record.user_id,
        title='续借成功',
        content=f'您借阅的《{record.book.title}》续借成功，新的到期日期为{record.due_date}',
        type='renew'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': '续借成功', 'record': record.to_dict()}), 200


@app.route('/api/borrow/<int:record_id>/return', methods=['POST'])
@jwt_required()
def return_book(record_id):
    identity = get_jwt_identity()
    record = BorrowRecord.query.get(record_id)
    if not record:
        return jsonify({'message': '借阅记录不存在'}), 404
    if identity['role'] not in ['admin', 'librarian'] and record.user_id != identity['id']:
        return jsonify({'message': '无权操作'}), 403
    if record.status == 'returned':
        return jsonify({'message': '图书已归还'}), 400

    record.return_date = date.today()
    record.status = 'returned'
    book = Book.query.get(record.book_id)
    if book:
        book.available_stock += 1
    db.session.commit()
    return jsonify({'message': '归还成功', 'record': record.to_dict()}), 200


@app.route('/api/borrow/my', methods=['GET'])
@jwt_required()
def get_my_borrows():
    identity = get_jwt_identity()
    records = BorrowRecord.query.filter_by(user_id=identity['id']) \
        .order_by(BorrowRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records]), 200


@app.route('/api/borrow/records', methods=['GET'])
@jwt_required()
def get_all_borrows():
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        records = BorrowRecord.query.filter_by(user_id=identity['id']).all()
    else:
        records = BorrowRecord.query.order_by(BorrowRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records]), 200


@app.route('/api/borrow/scan', methods=['POST'])
@jwt_required()
def scan_borrow():
    identity = get_jwt_identity()
    data = request.get_json() or {}
    qr_data = data.get('qr_data', '')
    if not qr_data.startswith('BOOK:'):
        return jsonify({'message': '无效的二维码格式'}), 400
    try:
        book_id = int(qr_data.split(':')[1])
    except:
        return jsonify({'message': '无效的二维码'}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    if book.available_stock <= 0:
        return jsonify({'message': '库存不足'}), 400

    active = BorrowRecord.query.filter(
        BorrowRecord.user_id == identity['id'],
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    if active >= Config.MAX_BORROW_COUNT:
        return jsonify({'message': '已达到最大借阅数量'}), 400

    today = date.today()
    record = BorrowRecord(
        user_id=identity['id'],
        book_id=book.id,
        borrow_date=today,
        due_date=today + timedelta(days=Config.BORROW_DAYS)
    )
    book.available_stock -= 1
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': '借阅成功', 'record': record.to_dict()}), 200


@app.route('/api/borrow/scan/return', methods=['POST'])
@jwt_required()
def scan_return():
    identity = get_jwt_identity()
    data = request.get_json() or {}
    qr_data = data.get('qr_data', '')
    if not qr_data.startswith('BOOK:'):
        return jsonify({'message': '无效的二维码'}), 400
    try:
        book_id = int(qr_data.split(':')[1])
    except:
        return jsonify({'message': '无效的二维码'}), 400

    record = BorrowRecord.query.filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.user_id == identity['id'],
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).first()
    if not record:
        return jsonify({'message': '未找到借阅记录'}), 404

    record.return_date = date.today()
    record.status = 'returned'
    book = Book.query.get(record.book_id)
    if book:
        book.available_stock += 1
    db.session.commit()
    return jsonify({'message': '归还成功', 'record': record.to_dict()}), 200


# ----- Recommendations -----

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    identity = get_jwt_identity()
    recs = Recommendation.query.filter_by(user_id=identity['id']) \
        .order_by(Recommendation.score.desc()).limit(10).all()
    return jsonify([r.to_dict() for r in recs]), 200


@app.route('/api/recommendations/generate', methods=['POST'])
@jwt_required()
def generate_recommendations():
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    Recommendation.query.filter_by(user_id=user_id).delete()

    all_books = Book.query.all()
    results = []
    for book in all_books:
        score = 0
        reasons = []
        if user.major and book.category and user.major in book.category:
            score += 30
            reasons.append('专业匹配')
        if book.keywords and user.major and user.major in book.keywords:
            score += 20
            reasons.append('关键词匹配')
        user_borrows = BorrowRecord.query.filter_by(
            user_id=user_id, book_id=book.id).count()
        if user_borrows > 0:
            score += 15
            reasons.append('曾借阅过')
        if book.available_stock > 0:
            score += 10
        if score > 0:
            results.append({'book_id': book.id, 'score': score,
                            'reason': '；'.join(reasons)})

    results.sort(key=lambda x: x['score'], reverse=True)
    for r in results[:10]:
        db.session.add(Recommendation(
            user_id=user_id, book_id=r['book_id'],
            score=r['score'], reason=r['reason']
        ))
    db.session.commit()
    return jsonify({'message': '推荐生成成功', 'count': len(results[:10])}), 200


# ----- Second Hand Books -----

@app.route('/api/second_hand', methods=['GET'])
def get_second_hand_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()

    query = SecondHandBook.query.filter_by(status='available')
    if keyword:
        query = query.filter(SecondHandBook.title.like(f'%{keyword}%'))

    pagination = query.order_by(SecondHandBook.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'books': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route('/api/second_hand', methods=['POST'])
@jwt_required()
def add_second_hand_book():
    identity = get_jwt_identity()
    data = request.get_json() or {}
    book = SecondHandBook(
        user_id=identity['id'],
        title=data.get('title', ''),
        author=data.get('author'),
        isbn=data.get('isbn'),
        condition=data.get('condition', 'good'),
        price=float(data.get('price', 0) or 0),
        description=data.get('description')
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': '二手图书发布成功', 'book': book.to_dict()}), 201


@app.route('/api/second_hand/<int:book_id>/buy', methods=['POST'])
@jwt_required()
def buy_second_hand_book(book_id):
    identity = get_jwt_identity()
    book = SecondHandBook.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    if book.status != 'available':
        return jsonify({'message': '图书已被预定或售出'}), 400
    if book.user_id == identity['id']:
        return jsonify({'message': '不能购买自己的图书'}), 400

    transaction = SecondHandTransaction(
        book_id=book.id,
        buyer_id=identity['id'],
        seller_id=book.user_id,
        transaction_date=date.today()
    )
    book.status = 'reserved'
    db.session.add(transaction)

    notif = Notification(
        user_id=book.user_id,
        title='二手图书交易',
        content=f'您发布的《{book.title}》有人想要购买，请及时联系买家确认交易。',
        type='transaction'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': '交易申请已提交', 'transaction': transaction.to_dict()}), 200


@app.route('/api/second_hand/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    identity = get_jwt_identity()
    txs = SecondHandTransaction.query.filter(
        db.or_(SecondHandTransaction.buyer_id == identity['id'],
               SecondHandTransaction.seller_id == identity['id'])
    ).all()
    return jsonify([t.to_dict() for t in txs]), 200


@app.route('/api/second_hand/transactions/<int:tx_id>/complete', methods=['PUT'])
@jwt_required()
def complete_transaction(tx_id):
    identity = get_jwt_identity()
    tx = SecondHandTransaction.query.get(tx_id)
    if not tx:
        return jsonify({'message': '交易记录不存在'}), 404
    if tx.seller_id != identity['id'] and tx.buyer_id != identity['id']:
        return jsonify({'message': '无权操作'}), 403

    tx.status = 'completed'
    book = SecondHandBook.query.get(tx.book_id)
    if book:
        book.status = 'sold'
    db.session.commit()
    return jsonify({'message': '交易完成'}), 200


# ----- Reading Records -----

@app.route('/api/reading', methods=['POST'])
@jwt_required()
def add_reading_record():
    identity = get_jwt_identity()
    data = request.get_json() or {}
    book_id = data.get('book_id')
    minutes = int(data.get('minutes', 0) or 0)

    if minutes <= 0:
        return jsonify({'message': '阅读时长必须大于0'}), 400
    if not Book.query.get(book_id):
        return jsonify({'message': '图书不存在'}), 404

    today = date.today()
    existing = ReadingRecord.query.filter(
        ReadingRecord.user_id == identity['id'],
        ReadingRecord.book_id == book_id,
        ReadingRecord.reading_date == today
    ).first()
    if existing:
        existing.minutes += minutes
    else:
        db.session.add(ReadingRecord(
            user_id=identity['id'], book_id=book_id,
            reading_date=today, minutes=minutes
        ))

    user = User.query.get(identity['id'])
    user.total_reading_minutes = (user.total_reading_minutes or 0) + minutes
    db.session.commit()
    return jsonify({'message': '阅读记录添加成功'}), 200


@app.route('/api/reading/stats', methods=['GET'])
@jwt_required()
def get_reading_stats():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    total_minutes = user.total_reading_minutes or 0

    rows = db.session.query(
        db.func.strftime('%Y-%m', ReadingRecord.reading_date).label('month'),
        db.func.sum(ReadingRecord.minutes).label('total_minutes')
    ).filter(ReadingRecord.user_id == identity['id']) \
     .group_by('month').all()

    monthly_stats = [{'month': r[0], 'minutes': int(r[1])} for r in rows]
    return jsonify({'total_minutes': total_minutes,
                    'monthly_stats': monthly_stats}), 200


# ----- Admin / Stats -----

@app.route('/api/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    total_books = Book.query.count()
    total_users = User.query.filter_by(role='student').count()
    total_borrowed = BorrowRecord.query.filter(
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    overdue_count = BorrowRecord.query.filter_by(status='overdue').count()
    active_alerts = StockAlert.query.filter_by(status='active').count()

    return jsonify({
        'total_books': total_books,
        'total_users': total_users,
        'total_borrowed': total_borrowed,
        'overdue_count': overdue_count,
        'active_alerts': active_alerts
    }), 200


@app.route('/api/stats/class', methods=['GET'])
@jwt_required()
def get_class_stats():
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403

    rows = db.session.query(
        User.major,
        db.func.count(User.id).label('total_users'),
        db.func.sum(User.total_reading_minutes).label('total_reading_minutes'),
        db.func.count(BorrowRecord.id).label('total_borrows')
    ).outerjoin(BorrowRecord, User.id == BorrowRecord.user_id) \
     .filter(User.major.isnot(None)) \
     .group_by(User.major).all()

    return jsonify([{
        'major': r[0],
        'total_users': int(r[1]),
        'total_reading_minutes': int(r[2] or 0),
        'total_borrows': int(r[3] or 0)
    } for r in rows]), 200


# ----- Stock Alerts -----

@app.route('/api/stock_alerts', methods=['GET'])
@jwt_required()
def get_stock_alerts():
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    alerts = StockAlert.query.filter_by(status='active').all()
    return jsonify([a.to_dict() for a in alerts]), 200


@app.route('/api/stock_alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    alert = StockAlert.query.get(alert_id)
    if not alert:
        return jsonify({'message': '预警不存在'}), 404
    alert.status = 'resolved'
    db.session.commit()
    return jsonify({'message': '已处理'}), 200


# ----- Book Requests -----

@app.route('/api/book_requests', methods=['GET'])
@jwt_required()
def get_book_requests():
    identity = get_jwt_identity()
    if identity['role'] in ['admin', 'librarian']:
        reqs = BookRequest.query.order_by(BookRequest.created_at.desc()).all()
    else:
        reqs = BookRequest.query.filter_by(user_id=identity['id']).all()
    return jsonify([r.to_dict() for r in reqs]), 200


@app.route('/api/book_requests', methods=['POST'])
@jwt_required()
def create_book_request():
    identity = get_jwt_identity()
    data = request.get_json() or {}
    req = BookRequest(
        user_id=identity['id'],
        title=data.get('title', ''),
        author=data.get('author'),
        isbn=data.get('isbn'),
        reason=data.get('reason')
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({'message': '采购申请已提交', 'request': req.to_dict()}), 201


@app.route('/api/book_requests/<int:req_id>', methods=['PUT'])
@jwt_required()
def update_book_request(req_id):
    identity = get_jwt_identity()
    if identity['role'] not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    req = BookRequest.query.get(req_id)
    if not req:
        return jsonify({'message': '申请不存在'}), 404
    data = request.get_json() or {}
    if 'status' in data:
        req.status = data['status']
    db.session.commit()
    return jsonify({'message': '状态已更新', 'request': req.to_dict()}), 200


# ----- Notifications -----

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    identity = get_jwt_identity()
    notifs = Notification.query.filter_by(user_id=identity['id']) \
        .order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifs]), 200


@app.route('/api/notifications/read_all', methods=['POST'])
@jwt_required()
def mark_all_read():
    identity = get_jwt_identity()
    Notification.query.filter_by(user_id=identity['id'], read=False) \
        .update({'read': True})
    db.session.commit()
    return jsonify({'message': '已全部标记为已读'}), 200


# ==================== Seed Data ====================

def seed_data():
    if User.query.count() > 0:
        return

    users = [
        User(username='admin', password=hash_password('password'),
             real_name='管理员', role='admin',
             student_id='ADMIN001', email='admin@library.edu', phone='13800000000'),
        User(username='librarian', password=hash_password('password'),
             real_name='图书管理员', role='librarian',
             student_id='LIB001', email='librarian@library.edu', phone='13800000001'),
        User(username='student1', password=hash_password('password'),
             real_name='张三', role='student', major='计算机科学',
             student_id='2021001', email='zhangsan@library.edu', phone='13800000002',
             total_reading_minutes=120),
        User(username='student2', password=hash_password('password'),
             real_name='李四', role='student', major='软件工程',
             student_id='2021002', email='lisi@library.edu', phone='13800000003',
             total_reading_minutes=240),
        User(username='student3', password=hash_password('password'),
             real_name='王五', role='student', major='数据科学',
             student_id='2021003', email='wangwu@library.edu', phone='13800000004',
             total_reading_minutes=360),
    ]
    db.session.add_all(users)
    db.session.flush()

    books = [
        Book(isbn='978-7-111-53551-1', title='Python编程：从入门到实践',
             author='Eric Matthes', publisher='人民邮电出版社',
             category='编程', location='A区-1排-001',
             total_stock=10, available_stock=8, price=89.0,
             description='针对所有层次Python读者的经典编程入门书籍',
             keywords='Python,编程入门,计算机科学'),
        Book(isbn='978-7-115-42857-7', title='JavaScript高级程序设计',
             author='Nicholas C. Zakas', publisher='人民邮电出版社',
             category='编程', location='A区-1排-002',
             total_stock=8, available_stock=5, price=129.0,
             description='JavaScript权威指南',
             keywords='JavaScript,前端,软件工程'),
        Book(isbn='978-7-302-41580-7', title='数据结构与算法分析',
             author='Mark Allen Weiss', publisher='清华大学出版社',
             category='计算机', location='B区-2排-001',
             total_stock=6, available_stock=3, price=69.0,
             description='数据结构与算法经典教材',
             keywords='数据结构,算法,计算机科学'),
        Book(isbn='978-7-111-40701-0', title='算法导论',
             author='Thomas H. Cormen', publisher='机械工业出版社',
             category='计算机', location='B区-2排-002',
             total_stock=5, available_stock=2, price=128.0,
             description='算法领域的经典教材',
             keywords='算法,计算机,数据结构'),
        Book(isbn='978-7-115-37064-3', title='深入浅出数据分析',
             author='Michael Milton', publisher='人民邮电出版社',
             category='数据分析', location='C区-3排-001',
             total_stock=4, available_stock=4, price=59.0,
             description='数据分析入门书籍',
             keywords='数据分析,数据科学'),
        Book(isbn='978-7-111-58165-5', title='深度学习',
             author='Ian Goodfellow', publisher='人民邮电出版社',
             category='人工智能', location='C区-3排-002',
             total_stock=3, available_stock=1, price=199.0,
             description='深度学习领域的经典教材',
             keywords='深度学习,AI,人工智能,数据科学'),
        Book(isbn='978-7-302-50754-1', title='机器学习',
             author='周志华', publisher='清华大学出版社',
             category='人工智能', location='C区-3排-003',
             total_stock=5, available_stock=3, price=89.0,
             description='机器学习入门经典',
             keywords='机器学习,AI,数据科学'),
        Book(isbn='978-7-111-60022-4', title='Vue.js设计与实现',
             author='霍春阳', publisher='机械工业出版社',
             category='编程', location='A区-1排-003',
             total_stock=4, available_stock=2, price=119.0,
             description='Vue.js核心原理详解',
             keywords='Vue.js,前端,软件工程'),
        Book(isbn='978-7-5086-5856-5', title='经济学原理',
             author='曼昆', publisher='北京大学出版社',
             category='经济学', location='D区-4排-001',
             total_stock=8, available_stock=6, price=68.0,
             description='经济学入门经典教材',
             keywords='经济学'),
        Book(isbn='978-7-04-045103-3', title='高等数学',
             author='同济大学', publisher='高等教育出版社',
             category='数学', location='E区-5排-001',
             total_stock=15, available_stock=10, price=59.0,
             description='高等数学经典教材',
             keywords='高等数学,数学'),
    ]
    db.session.add_all(books)
    db.session.flush()

    today = date.today()
    borrows = [
        BorrowRecord(user_id=users[2].id, book_id=books[0].id,
                     borrow_date=today - timedelta(days=10),
                     due_date=today + timedelta(days=20), status='borrowed'),
        BorrowRecord(user_id=users[2].id, book_id=books[2].id,
                     borrow_date=today - timedelta(days=20),
                     due_date=today + timedelta(days=10), status='borrowed'),
        BorrowRecord(user_id=users[3].id, book_id=books[1].id,
                     borrow_date=today - timedelta(days=35),
                     due_date=today - timedelta(days=5), status='overdue',
                     fine=2.5),
        BorrowRecord(user_id=users[4].id, book_id=books[4].id,
                     borrow_date=today - timedelta(days=15),
                     due_date=today + timedelta(days=15), status='borrowed'),
        BorrowRecord(user_id=users[4].id, book_id=books[6].id,
                     borrow_date=today - timedelta(days=60),
                     return_date=today - timedelta(days=40),
                     due_date=today - timedelta(days=30), status='returned'),
    ]
    db.session.add_all(borrows)

    # 调整库存
    books[0].available_stock = 7
    books[2].available_stock = 2
    books[1].available_stock = 4
    books[4].available_stock = 3
    books[6].available_stock = 3

    # 阅读记录
    db.session.add_all([
        ReadingRecord(user_id=users[2].id, book_id=books[0].id,
                      reading_date=today - timedelta(days=5), minutes=60),
        ReadingRecord(user_id=users[2].id, book_id=books[0].id,
                      reading_date=today - timedelta(days=3), minutes=45),
        ReadingRecord(user_id=users[2].id, book_id=books[2].id,
                      reading_date=today - timedelta(days=4), minutes=90),
        ReadingRecord(user_id=users[3].id, book_id=books[1].id,
                      reading_date=today - timedelta(days=10), minutes=30),
        ReadingRecord(user_id=users[4].id, book_id=books[4].id,
                      reading_date=today - timedelta(days=7), minutes=75),
        ReadingRecord(user_id=users[4].id, book_id=books[6].id,
                      reading_date=today - timedelta(days=50), minutes=60),
    ])

    # 二手图书
    db.session.add_all([
        SecondHandBook(user_id=users[2].id, title='Python编程：从入门到实践',
                       author='Eric Matthes', isbn='978-7-111-53551-1',
                       condition='good', price=45.0,
                       description='已阅读完毕，状态良好'),
        SecondHandBook(user_id=users[3].id, title='JavaScript高级程序设计',
                       author='Nicholas C. Zakas', isbn='978-7-115-42857-7',
                       condition='like_new', price=80.0,
                       description='全新未拆封'),
        SecondHandBook(user_id=users[4].id, title='数据结构与算法分析',
                       author='Mark Allen Weiss', isbn='978-7-302-41580-7',
                       condition='fair', price=30.0,
                       description='有少量笔记'),
    ])

    # 库存预警
    db.session.add_all([
        StockAlert(book_id=books[3].id, threshold=5, current_stock=2),
        StockAlert(book_id=books[5].id, threshold=5, current_stock=1),
    ])

    # 采购申请
    db.session.add_all([
        BookRequest(user_id=users[2].id, title='Python Cookbook',
                    author='David Beazley', isbn='978-7-111-47005-7',
                    reason='课程学习需要', status='pending'),
        BookRequest(user_id=users[3].id, title='设计模式',
                    author='Erich Gamma', isbn='978-7-111-07554-7',
                    reason='毕业设计参考', status='approved'),
    ])

    # 通知
    db.session.add_all([
        Notification(user_id=users[3].id, title='图书逾期提醒',
                     content='您借阅的《JavaScript高级程序设计》已逾期5天，请尽快归还！',
                     type='overdue'),
        Notification(user_id=users[2].id, title='借阅成功',
                     content='您已成功借阅《Python编程：从入门到实践》，请于到期前归还或续借。',
                     type='system'),
    ])

    # 推荐
    db.session.add_all([
        Recommendation(user_id=users[2].id, book_id=books[5].id, score=50,
                       reason='专业匹配；关键词匹配'),
        Recommendation(user_id=users[2].id, book_id=books[3].id, score=40,
                       reason='专业匹配'),
        Recommendation(user_id=users[3].id, book_id=books[7].id, score=50,
                       reason='关键词匹配'),
    ])

    db.session.commit()
    print('数据库初始化完成，测试数据已载入')


with app.app_context():
    db.create_all()
    seed_data()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
