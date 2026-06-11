from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import app, db, Config
from models import User, Book, BorrowRecord, Course, UserCourse, Recommendation, \
    SecondHandBook, SecondHandTransaction, ReadingRecord, StockAlert, BookRequest, Notification
from datetime import date, timedelta
import bcrypt
import qrcode
from io import BytesIO
import base64

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': '用户名不存在'}), 401
    
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'message': '密码错误'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    if User.query.filter_by(student_id=data.get('student_id')).first():
        return jsonify({'message': '学号已被注册'}), 400
    
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    user = User(
        username=data['username'],
        password=hashed_password.decode('utf-8'),
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
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': '用户不存在'}), 404

@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    
    query = Book.query
    if keyword:
        query = query.filter(Book.title.ilike(f'%{keyword}%') | Book.author.ilike(f'%{keyword}%'))
    if category:
        query = query.filter(Book.category == category)
    
    pagination = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
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
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    book = Book(
        isbn=data['isbn'],
        title=data['title'],
        author=data.get('author'),
        publisher=data.get('publisher'),
        publish_date=data.get('publish_date'),
        category=data.get('category'),
        location=data.get('location'),
        total_stock=data.get('total_stock', 0),
        available_stock=data.get('available_stock', 0),
        price=data.get('price'),
        description=data.get('description'),
        keywords=data.get('keywords')
    )
    db.session.add(book)
    db.session.commit()
    
    return jsonify({'message': '图书添加成功', 'book': book.to_dict()}), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(book, key):
            setattr(book, key, value)
    
    db.session.commit()
    return jsonify({'message': '图书更新成功', 'book': book.to_dict()}), 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': '图书删除成功'}), 200

@app.route('/api/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    data = request.get_json()
    book_id = data.get('book_id')
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    
    if book.available_stock <= 0:
        return jsonify({'message': '库存不足'}), 400
    
    active_borrows = BorrowRecord.query.filter(
        BorrowRecord.user_id == user.id,
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    
    if active_borrows >= Config.MAX_BORROW_COUNT:
        return jsonify({'message': '已达到最大借阅数量'}), 400
    
    today = date.today()
    due_date = today + timedelta(days=Config.BORROW_DAYS)
    
    borrow_record = BorrowRecord(
        user_id=user.id,
        book_id=book.id,
        borrow_date=today,
        due_date=due_date
    )
    
    book.available_stock -= 1
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify({'message': '借阅成功', 'record': borrow_record.to_dict()}), 200

@app.route('/api/borrow/<int:record_id>/renew', methods=['POST'])
@jwt_required()
def renew_book(record_id):
    current_user = get_jwt_identity()
    
    record = BorrowRecord.query.get(record_id)
    if not record:
        return jsonify({'message': '借阅记录不存在'}), 404
    
    if record.user_id != current_user['id']:
        return jsonify({'message': '无权操作'}), 403
    
    if record.status == 'returned':
        return jsonify({'message': '图书已归还，无法续借'}), 400
    
    if record.renew_count >= Config.MAX_RENEW_COUNT:
        return jsonify({'message': '已达到最大续借次数'}), 400
    
    record.due_date += timedelta(days=Config.BORROW_DAYS)
    record.renew_count += 1
    record.status = 'renewed'
    
    notification = Notification(
        user_id=record.user_id,
        title='续借成功',
        content=f'您借阅的《{record.book.title}》续借成功，新的到期日期为{record.due_date}',
        type='renew'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': '续借成功', 'record': record.to_dict()}), 200

@app.route('/api/borrow/<int:record_id>/return', methods=['POST'])
@jwt_required()
def return_book(record_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    record = BorrowRecord.query.get(record_id)
    if not record:
        return jsonify({'message': '借阅记录不存在'}), 404
    
    if user.role not in ['admin', 'librarian'] and record.user_id != current_user['id']:
        return jsonify({'message': '无权操作'}), 403
    
    if record.status == 'returned':
        return jsonify({'message': '图书已归还'}), 400
    
    record.return_date = date.today()
    record.status = 'returned'
    
    book = Book.query.get(record.book_id)
    book.available_stock += 1
    
    db.session.commit()
    return jsonify({'message': '归还成功', 'record': record.to_dict()}), 200

@app.route('/api/borrow/scan', methods=['POST'])
@jwt_required()
def scan_borrow():
    data = request.get_json()
    qr_data = data.get('qr_data')
    
    if not qr_data:
        return jsonify({'message': '请扫描二维码'}), 400
    
    parts = qr_data.split(':')
    if len(parts) != 2:
        return jsonify({'message': '无效的二维码'}), 400
    
    book_id = int(parts[1])
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    active_borrows = BorrowRecord.query.filter(
        BorrowRecord.user_id == user.id,
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    
    if active_borrows >= Config.MAX_BORROW_COUNT:
        return jsonify({'message': '已达到最大借阅数量'}), 400
    
    today = date.today()
    due_date = today + timedelta(days=Config.BORROW_DAYS)
    
    borrow_record = BorrowRecord(
        user_id=user.id,
        book_id=book.id,
        borrow_date=today,
        due_date=due_date
    )
    
    book.available_stock -= 1
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify({'message': '借阅成功', 'record': borrow_record.to_dict()}), 200

@app.route('/api/borrow/scan/return', methods=['POST'])
@jwt_required()
def scan_return():
    data = request.get_json()
    qr_data = data.get('qr_data')
    
    if not qr_data:
        return jsonify({'message': '请扫描二维码'}), 400
    
    parts = qr_data.split(':')
    if len(parts) != 2:
        return jsonify({'message': '无效的二维码'}), 400
    
    book_id = int(parts[1])
    
    record = BorrowRecord.query.filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).first()
    
    if not record:
        return jsonify({'message': '未找到借阅记录'}), 404
    
    record.return_date = date.today()
    record.status = 'returned'
    
    book = Book.query.get(record.book_id)
    book.available_stock += 1
    
    db.session.commit()
    return jsonify({'message': '归还成功', 'record': record.to_dict()}), 200

@app.route('/api/books/<int:book_id>/qr', methods=['GET'])
def get_book_qr(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': '图书不存在'}), 404
    
    qr_data = f'BOOK:{book_id}'
    qr_base64 = generate_qr_code(qr_data)
    
    return jsonify({
        'book_id': book.id,
        'title': book.title,
        'qr_code': f'data:image/png;base64,{qr_base64}'
    }), 200

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    recommendations = Recommendation.query.filter(
        Recommendation.user_id == user.id
    ).order_by(Recommendation.score.desc()).limit(10).all()
    
    return jsonify([rec.to_dict() for rec in recommendations]), 200

@app.route('/api/recommendations/generate', methods=['POST'])
@jwt_required()
def generate_recommendations():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    Recommendation.query.filter(Recommendation.user_id == user.id).delete()
    
    user_courses = UserCourse.query.filter(UserCourse.user_id == user.id).all()
    course_names = [uc.course.course_name for uc in user_courses]
    
    all_books = Book.query.all()
    recommendations = []
    
    for book in all_books:
        score = 0
        reason = []
        
        if user.major and book.category:
            if user.major in book.category or book.category in user.major:
                score += 30
                reason.append('专业匹配')
        
        if book.keywords:
            keywords = book.keywords.split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                for course_name in course_names:
                    if keyword in course_name or course_name in keyword:
                        score += 20
                        reason.append(f'课程匹配：{course_name}')
                        break
        
        user_borrows = BorrowRecord.query.filter(
            BorrowRecord.user_id == user.id,
            BorrowRecord.book_id == book.id
        ).count()
        if user_borrows > 0:
            score += 15
            reason.append('曾借阅过')
        
        if book.available_stock > 0:
            score += 10
        
        if score > 0:
            recommendations.append({
                'book_id': book.id,
                'score': score,
                'reason': '；'.join(reason)
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    for rec in recommendations[:10]:
        recommendation = Recommendation(
            user_id=user.id,
            book_id=rec['book_id'],
            score=rec['score'],
            reason=rec['reason']
        )
        db.session.add(recommendation)
    
    db.session.commit()
    
    return jsonify({'message': '推荐生成成功', 'count': len(recommendations[:10])}), 200

@app.route('/api/second_hand', methods=['GET'])
def get_second_hand_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    
    query = SecondHandBook.query.filter(SecondHandBook.status == 'available')
    if keyword:
        query = query.filter(SecondHandBook.title.ilike(f'%{keyword}%'))
    
    pagination = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@app.route('/api/second_hand', methods=['POST'])
@jwt_required()
def add_second_hand_book():
    current_user = get_jwt_identity()
    
    data = request.get_json()
    book = SecondHandBook(
        user_id=current_user['id'],
        title=data['title'],
        author=data.get('author'),
        isbn=data.get('isbn'),
        condition=data.get('condition', 'good'),
        price=data['price'],
        description=data.get('description')
    )
    db.session.add(book)
    db.session.commit()
    
    return jsonify({'message': '二手图书发布成功', 'book': book.to_dict()}), 201

@app.route('/api/second_hand/<int:book_id>', methods=['GET'])
def get_second_hand_book(book_id):
    book = SecondHandBook.query.get(book_id)
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({'message': '二手图书不存在'}), 404

@app.route('/api/second_hand/<int:book_id>/buy', methods=['POST'])
@jwt_required()
def buy_second_hand_book(book_id):
    current_user = get_jwt_identity()
    
    book = SecondHandBook.query.get(book_id)
    if not book:
        return jsonify({'message': '二手图书不存在'}), 404
    
    if book.status != 'available':
        return jsonify({'message': '图书已被预定或售出'}), 400
    
    if book.user_id == current_user['id']:
        return jsonify({'message': '不能购买自己的图书'}), 400
    
    transaction = SecondHandTransaction(
        book_id=book.id,
        buyer_id=current_user['id'],
        seller_id=book.user_id
    )
    
    book.status = 'reserved'
    db.session.add(transaction)
    db.session.commit()
    
    notification = Notification(
        user_id=book.user_id,
        title='二手图书交易',
        content=f'您发布的《{book.title}》有人想要购买，请及时联系买家确认交易',
        type='transaction'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': '交易申请已提交', 'transaction': transaction.to_dict()}), 200

@app.route('/api/second_hand/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user = get_jwt_identity()
    
    transactions = SecondHandTransaction.query.filter(
        (SecondHandTransaction.buyer_id == current_user['id']) |
        (SecondHandTransaction.seller_id == current_user['id'])
    ).all()
    
    return jsonify([t.to_dict() for t in transactions]), 200

@app.route('/api/reading', methods=['POST'])
@jwt_required()
def add_reading_record():
    current_user = get_jwt_identity()
    
    data = request.get_json()
    book_id = data.get('book_id')
    minutes = data.get('minutes', 0)
    
    if minutes <= 0:
        return jsonify({'message': '阅读时长必须大于0'}), 400
    
    today = date.today()
    existing_record = ReadingRecord.query.filter(
        ReadingRecord.user_id == current_user['id'],
        ReadingRecord.book_id == book_id,
        ReadingRecord.reading_date == today
    ).first()
    
    if existing_record:
        existing_record.minutes += minutes
    else:
        reading_record = ReadingRecord(
            user_id=current_user['id'],
            book_id=book_id,
            reading_date=today,
            minutes=minutes
        )
        db.session.add(reading_record)
    
    user = User.query.get(current_user['id'])
    user.total_reading_minutes += minutes
    
    db.session.commit()
    return jsonify({'message': '阅读记录添加成功'}), 200

@app.route('/api/reading/stats', methods=['GET'])
@jwt_required()
def get_reading_stats():
    current_user = get_jwt_identity()
    
    total_minutes = db.session.query(
        db.func.sum(ReadingRecord.minutes)
    ).filter(ReadingRecord.user_id == current_user['id']).scalar() or 0
    
    monthly_stats = db.session.query(
        db.func.date_format(ReadingRecord.reading_date, '%Y-%m').label('month'),
        db.func.sum(ReadingRecord.minutes).label('total_minutes')
    ).filter(ReadingRecord.user_id == current_user['id']).group_by('month').all()
    
    return jsonify({
        'total_minutes': total_minutes,
        'monthly_stats': [{'month': m[0], 'minutes': m[1]} for m in monthly_stats]
    }), 200

@app.route('/api/stats/class', methods=['GET'])
@jwt_required()
def get_class_stats():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    class_stats = db.session.query(
        User.major,
        db.func.count(User.id).label('total_users'),
        db.func.sum(User.total_reading_minutes).label('total_reading_minutes'),
        db.func.count(BorrowRecord.id).label('total_borrows')
    ).outerjoin(BorrowRecord, User.id == BorrowRecord.user_id)\
     .group_by(User.major).all()
    
    return jsonify([{
        'major': s[0],
        'total_users': s[1],
        'total_reading_minutes': s[2] or 0,
        'total_borrows': s[3] or 0
    } for s in class_stats]), 200

@app.route('/api/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    total_books = Book.query.count()
    total_users = User.query.filter(User.role == 'student').count()
    total_borrowed = BorrowRecord.query.filter(
        BorrowRecord.status.in_(['borrowed', 'overdue', 'renewed'])
    ).count()
    overdue_count = BorrowRecord.query.filter(BorrowRecord.status == 'overdue').count()
    active_alerts = StockAlert.query.filter(StockAlert.status == 'active').count()
    
    return jsonify({
        'total_books': total_books,
        'total_users': total_users,
        'total_borrowed': total_borrowed,
        'overdue_count': overdue_count,
        'active_alerts': active_alerts
    }), 200

@app.route('/api/stock_alerts', methods=['GET'])
@jwt_required()
def get_stock_alerts():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    alerts = StockAlert.query.filter(StockAlert.status == 'active').all()
    return jsonify([alert.to_dict() for alert in alerts]), 200

@app.route('/api/stock_alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_stock_alert(alert_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    alert = StockAlert.query.get(alert_id)
    if not alert:
        return jsonify({'message': '预警不存在'}), 404
    
    alert.status = 'resolved'
    db.session.commit()
    
    return jsonify({'message': '预警已处理'}), 200

@app.route('/api/book_requests', methods=['GET'])
@jwt_required()
def get_book_requests():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role in ['admin', 'librarian']:
        requests = BookRequest.query.all()
    else:
        requests = BookRequest.query.filter(BookRequest.user_id == current_user['id']).all()
    
    return jsonify([req.to_dict() for req in requests]), 200

@app.route('/api/book_requests', methods=['POST'])
@jwt_required()
def create_book_request():
    current_user = get_jwt_identity()
    
    data = request.get_json()
    book_request = BookRequest(
        user_id=current_user['id'],
        title=data['title'],
        author=data.get('author'),
        isbn=data.get('isbn'),
        reason=data.get('reason')
    )
    db.session.add(book_request)
    db.session.commit()
    
    return jsonify({'message': '图书采购申请已提交', 'request': book_request.to_dict()}), 201

@app.route('/api/book_requests/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_book_request(request_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role not in ['admin', 'librarian']:
        return jsonify({'message': '权限不足'}), 403
    
    book_request = BookRequest.query.get(request_id)
    if not book_request:
        return jsonify({'message': '申请不存在'}), 404
    
    data = request.get_json()
    if 'status' in data:
        book_request.status = data['status']
    
    db.session.commit()
    return jsonify({'message': '申请状态已更新', 'request': book_request.to_dict()}), 200

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    
    notifications = Notification.query.filter(
        Notification.user_id == current_user['id']
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify([n.to_dict() for n in notifications]), 200

@app.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notif_id):
    current_user = get_jwt_identity()
    
    notification = Notification.query.get(notif_id)
    if not notification:
        return jsonify({'message': '通知不存在'}), 404
    
    if notification.user_id != current_user['id']:
        return jsonify({'message': '无权操作'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'message': '已标记为已读'}), 200

@app.route('/api/notifications/read_all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    current_user = get_jwt_identity()
    
    Notification.query.filter(
        Notification.user_id == current_user['id'],
        Notification.read == False
    ).update({'read': True})
    db.session.commit()
    
    return jsonify({'message': '所有通知已标记为已读'}), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Book.category).distinct().all()
    return jsonify([c[0] for c in categories if c[0]]), 200

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = User.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

def register_routes(app):
    pass