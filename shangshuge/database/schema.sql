CREATE DATABASE IF NOT EXISTS library_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE library_system;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    student_id VARCHAR(20) UNIQUE,
    major VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    role ENUM('admin', 'librarian', 'student') DEFAULT 'student',
    avatar_url VARCHAR(500),
    total_reading_minutes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_student_id (student_id),
    INDEX idx_role (role)
);

CREATE TABLE IF NOT EXISTS books (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    publisher VARCHAR(100),
    publish_date DATE,
    category VARCHAR(50),
    location VARCHAR(100),
    total_stock INT DEFAULT 0,
    available_stock INT DEFAULT 0,
    price DECIMAL(10,2),
    description TEXT,
    cover_url VARCHAR(500),
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_isbn (isbn),
    INDEX idx_title (title),
    INDEX idx_category (category),
    INDEX idx_available_stock (available_stock)
);

CREATE TABLE IF NOT EXISTS borrow_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status ENUM('borrowed', 'returned', 'overdue', 'renewed') DEFAULT 'borrowed',
    renew_count INT DEFAULT 0,
    fine DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

CREATE TABLE IF NOT EXISTS courses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(50) UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    credit INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_course_code (course_code),
    INDEX idx_department (department)
);

CREATE TABLE IF NOT EXISTS user_courses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    enrollment_date DATE,
    grade VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_course (user_id, course_id),
    INDEX idx_user_id (user_id),
    INDEX idx_course_id (course_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    score DECIMAL(5,2) DEFAULT 0,
    reason TEXT,
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book (user_id, book_id),
    INDEX idx_user_id (user_id),
    INDEX idx_score (score)
);

CREATE TABLE IF NOT EXISTS second_hand_books (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    book_id BIGINT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    isbn VARCHAR(20),
    condition ENUM('like_new', 'good', 'fair', 'poor') DEFAULT 'good',
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    cover_url VARCHAR(500),
    status ENUM('available', 'reserved', 'sold') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_condition (condition)
);

CREATE TABLE IF NOT EXISTS second_hand_transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    book_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    transaction_date DATE,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES second_hand_books(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_book_id (book_id),
    INDEX idx_buyer_id (buyer_id),
    INDEX idx_seller_id (seller_id),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS reading_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    reading_date DATE NOT NULL,
    minutes INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_reading_record (user_id, book_id, reading_date),
    INDEX idx_user_id (user_id),
    INDEX idx_reading_date (reading_date)
);

CREATE TABLE IF NOT EXISTS stock_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    book_id BIGINT NOT NULL,
    threshold INT DEFAULT 5,
    current_stock INT NOT NULL,
    status ENUM('active', 'resolved') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    INDEX idx_book_id (book_id),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS book_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    isbn VARCHAR(20),
    reason TEXT,
    status ENUM('pending', 'approved', 'rejected', 'purchased') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    type ENUM('overdue', 'renew', 'recommendation', 'transaction', 'system') DEFAULT 'system',
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_read (read),
    INDEX idx_created_at (created_at)
);

INSERT INTO users (username, password, real_name, student_id, major, email, phone, role) VALUES
('admin', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q', '管理员', 'ADMIN001', '图书馆', 'admin@library.edu', '13800138000', 'admin'),
('librarian', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q', '图书管理员', 'LIB001', '图书馆', 'librarian@library.edu', '13800138001', 'librarian'),
('student1', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q', '张三', '2021001', '计算机科学', 'zhangsan@student.edu', '13800138002', 'student'),
('student2', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q', '李四', '2021002', '软件工程', 'lisi@student.edu', '13800138003', 'student'),
('student3', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q', '王五', '2021003', '数据科学', 'wangwu@student.edu', '13800138004', 'student');

INSERT INTO books (isbn, title, author, publisher, publish_date, category, location, total_stock, available_stock, price, description, keywords) VALUES
('978-7-111-53551-5', 'Python编程：从入门到实践', 'Eric Matthes', '人民邮电出版社', '2016-07-01', '编程', 'A区-1排-001', 10, 8, 89.00, '针对所有层次Python读者的经典编程入门书籍', 'Python,编程入门'),
('978-7-115-42857-7', 'JavaScript高级程序设计', 'Nicholas C. Zakas', '人民邮电出版社', '2019-10-01', '编程', 'A区-1排-002', 8, 5, 129.00, 'JavaScript权威指南', 'JavaScript,前端'),
('978-7-302-41580-7', '数据结构与算法分析', 'Mark Allen Weiss', '清华大学出版社', '2014-01-01', '计算机', 'B区-2排-001', 6, 3, 69.00, '数据结构与算法经典教材', '数据结构,算法'),
('978-7-111-40701-0', '算法导论', 'Thomas H. Cormen', '机械工业出版社', '2012-08-01', '计算机', 'B区-2排-002', 5, 2, 128.00, '算法领域的经典教材', '算法,计算机'),
('978-7-115-37064-3', '深入浅出数据分析', 'Michael Milton', '人民邮电出版社', '2012-12-01', '数据分析', 'C区-3排-001', 4, 4, 59.00, '数据分析入门书籍', '数据分析'),
('978-7-111-58165-5', '深度学习', 'Ian Goodfellow', '人民邮电出版社', '2017-08-01', '人工智能', 'C区-3排-002', 3, 1, 199.00, '深度学习领域的经典教材', '深度学习,AI'),
('978-7-302-50754-1', '机器学习', '周志华', '清华大学出版社', '2016-01-01', '人工智能', 'C区-3排-003', 5, 3, 89.00, '机器学习入门经典', '机器学习'),
('978-7-111-60022-4', 'Vue.js设计与实现', '霍春阳', '机械工业出版社', '2022-01-01', '编程', 'A区-1排-003', 4, 2, 119.00, 'Vue.js核心原理详解', 'Vue.js,前端'),
('978-7-5086-5856-5', '经济学原理', '曼昆', '北京大学出版社', '2015-07-01', '经济学', 'D区-4排-001', 8, 6, 68.00, '经济学入门经典教材', '经济学'),
('978-7-04-045103-3', '高等数学', '同济大学', '高等教育出版社', '2014-07-01', '数学', 'E区-5排-001', 15, 10, 59.00, '高等数学经典教材', '高等数学');

INSERT INTO courses (course_code, course_name, department, credit) VALUES
('CS101', '计算机基础', '计算机学院', 3),
('CS102', '数据结构', '计算机学院', 4),
('CS103', '算法设计', '计算机学院', 4),
('CS201', '人工智能', '计算机学院', 3),
('SE101', '软件工程概论', '软件学院', 3),
('SE102', '数据库原理', '软件学院', 3),
('DS101', '数据分析', '数据科学学院', 3),
('DS102', '机器学习', '数据科学学院', 4);

INSERT INTO user_courses (user_id, course_id, enrollment_date, grade) VALUES
(3, 1, '2021-09-01', 'A'),
(3, 2, '2021-09-01', 'B'),
(3, 3, '2022-02-01', 'A'),
(4, 5, '2021-09-01', 'A'),
(4, 6, '2021-09-01', 'B'),
(5, 7, '2021-09-01', 'A'),
(5, 8, '2022-02-01', 'B');

INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, status) VALUES
(3, 1, '2024-05-01', '2024-06-01', 'borrowed'),
(3, 3, '2024-05-10', '2024-06-10', 'borrowed'),
(4, 2, '2024-04-15', '2024-05-15', 'overdue'),
(5, 5, '2024-05-05', '2024-06-05', 'borrowed'),
(5, 7, '2024-03-01', '2024-04-01', 'returned');

UPDATE books SET available_stock = available_stock - 1 WHERE id IN (1, 3, 2, 5, 7);
UPDATE books SET available_stock = available_stock + 1 WHERE id = 7;

INSERT INTO reading_records (user_id, book_id, reading_date, minutes) VALUES
(3, 1, '2024-05-15', 60),
(3, 1, '2024-05-16', 45),
(3, 3, '2024-05-17', 90),
(4, 2, '2024-04-20', 30),
(4, 2, '2024-04-21', 45),
(5, 5, '2024-05-06', 75),
(5, 7, '2024-03-10', 60);

INSERT INTO second_hand_books (user_id, title, author, isbn, condition, price, description, status) VALUES
(3, 'Python编程：从入门到实践', 'Eric Matthes', '978-7-111-53551-5', 'good', 45.00, '已阅读完毕，状态良好', 'available'),
(4, 'JavaScript高级程序设计', 'Nicholas C. Zakas', '978-7-115-42857-7', 'like_new', 80.00, '全新未拆封', 'available'),
(5, '数据结构与算法分析', 'Mark Allen Weiss', '978-7-302-41580-7', 'fair', 30.00, '有少量笔记', 'available');

INSERT INTO stock_alerts (book_id, threshold, current_stock, status) VALUES
(4, 5, 2, 'active'),
(6, 5, 1, 'active');

INSERT INTO book_requests (user_id, title, author, isbn, reason, status) VALUES
(3, 'Python Cookbook', 'David Beazley', '978-7-111-47005-7', '课程学习需要', 'pending'),
(4, '设计模式：可复用面向对象软件的基础', 'Erich Gamma', '978-7-111-07554-7', '毕业设计参考', 'approved');