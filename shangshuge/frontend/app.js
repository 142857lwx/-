var app = new Vue({
    el: '#app',
    data: {
        isLoggedIn: false,
        currentUser: {},
        currentPage: 'dashboard',
        loginTab: 'login',
        loginForm: { username: '', password: '' },
        registerForm: { username: '', password: '', real_name: '', student_id: '', major: '' },
        
        showNotification: false,
        notifications: [],
        unreadCount: 0,
        
        books: [],
        searchKeyword: '',
        searchCategory: '',
        categories: [],
        
        borrowRecords: [],
        myBorrows: [],
        maxRenewCount: 2,
        
        recommendations: [],
        secondhandBooks: [],
        secondhandKeyword: '',
        secondhandTransactions: [],
        myTransactions: [],
        
        readingStats: { total_minutes: 0, monthly_stats: [] },
        classStats: [],
        dashboardStats: { total_books: 0, total_users: 0, total_borrowed: 0, overdue_count: 0, active_alerts: 0 },
        topBooks: [],
        
        stockAlerts: [],
        bookRequests: [],
        readingRecords: [],
        users: [],
        
        showAddBook: false,
        editBookData: null,
        bookForm: { isbn: '', title: '', author: '', publisher: '', category: '', location: '', total_stock: 0, available_stock: 0, price: 0, description: '', keywords: '' },
        
        showAddSecondhand: false,
        secondhandForm: { title: '', author: '', isbn: '', condition: 'good', price: 0, description: '' },
        
        showAddReading: false,
        readingForm: { book_id: '', minutes: 0 },
        
        showAddRequest: false,
        requestForm: { title: '', author: '', isbn: '', reason: '' },
        
        scanData: '',
        nextId: { books: 11, users: 6, borrows: 6, secondhand: 4, transactions: 1, reading: 7, alerts: 3, requests: 3, notifications: 3, recommendations: 4 }
    },
    computed: {
        roleText() {
            const roles = { admin: '管理员', librarian: '图书管理员', student: '学生' };
            return roles[this.currentUser.role] || '未知';
        },
        pageTitle() {
            const titles = {
                dashboard: '数据看板',
                books: '图书管理',
                borrow: '借阅记录',
                recommend: '智能推荐',
                secondhand: '二手图书',
                reading: '阅读统计',
                stats: '班级统计',
                alerts: '库存预警',
                requests: '采购申请'
            };
            return titles[this.currentPage] || '图书系统';
        },
        filteredBooks() {
            return this.books.filter(book => {
                const matchKeyword = !this.searchKeyword || 
                    book.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                    book.author.toLowerCase().includes(this.searchKeyword.toLowerCase());
                const matchCategory = !this.searchCategory || book.category === this.searchCategory;
                return matchKeyword && matchCategory;
            });
        },
        visibleBorrowRecords() {
            if (this.currentUser.role === 'admin' || this.currentUser.role === 'librarian') {
                return this.borrowRecords;
            }
            return this.borrowRecords.filter(r => r.user_id === this.currentUser.id);
        },
        filteredSecondhandBooks() {
            return this.secondhandBooks.filter(book => {
                return !this.secondhandKeyword || 
                    book.title.toLowerCase().includes(this.secondhandKeyword.toLowerCase());
            });
        },
        activeAlerts() {
            return this.stockAlerts.filter(a => a.status === 'active');
        },
        visibleBookRequests() {
            if (this.currentUser.role === 'admin' || this.currentUser.role === 'librarian') {
                return this.bookRequests;
            }
            return this.bookRequests.filter(r => r.user_id === this.currentUser.id);
        }
    },
    mounted() {
        this.initData();
        const savedUser = localStorage.getItem('currentUser');
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.isLoggedIn = true;
            this.loadDashboard();
        }
    },
    methods: {
        initData() {
            let data = localStorage.getItem('libraryData');
            if (!data) {
                data = JSON.stringify(this.getDefaultData());
                localStorage.setItem('libraryData', data);
            }
            const libraryData = JSON.parse(data);
            this.books = libraryData.books;
            this.borrowRecords = libraryData.borrowRecords;
            this.secondhandBooks = libraryData.secondhandBooks;
            this.secondhandTransactions = libraryData.secondhandTransactions;
            this.readingRecords = libraryData.readingRecords;
            this.stockAlerts = libraryData.stockAlerts;
            this.bookRequests = libraryData.bookRequests;
            this.notifications = libraryData.notifications;
            this.recommendations = libraryData.recommendations;
            this.users = libraryData.users;
            this.categories = [...new Set(this.books.map(b => b.category).filter(Boolean))];
        },
        getDefaultData() {
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            const daysAgo = (days) => new Date(today.getTime() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            
            return {
                users: [
                    { id: 1, username: 'admin', password: 'admin', real_name: '管理员', role: 'admin', student_id: 'ADMIN001', email: 'admin@library.edu', phone: '13800000000', total_reading_minutes: 0 },
                    { id: 2, username: 'librarian', password: 'password', real_name: '图书管理员', role: 'librarian', student_id: 'LIB001', email: 'librarian@library.edu', phone: '13800000001', total_reading_minutes: 0 },
                    { id: 3, username: 'student1', password: 'password', real_name: '张三', role: 'student', major: '计算机科学', student_id: '2021001', email: 'zhangsan@library.edu', phone: '13800000002', total_reading_minutes: 120 },
                    { id: 4, username: 'student2', password: 'password', real_name: '李四', role: 'student', major: '软件工程', student_id: '2021002', email: 'lisi@library.edu', phone: '13800000003', total_reading_minutes: 240 },
                    { id: 5, username: 'student3', password: 'password', real_name: '王五', role: 'student', major: '数据科学', student_id: '2021003', email: 'wangwu@library.edu', phone: '13800000004', total_reading_minutes: 360 },
                ],
                books: [
                    { id: 1, isbn: '978-7-111-53551-1', title: 'Python编程：从入门到实践', author: 'Eric Matthes', publisher: '人民邮电出版社', category: '编程', location: 'A区-1排-001', total_stock: 10, available_stock: 7, price: 89.0, description: '针对所有层次Python读者的经典编程入门书籍', keywords: 'Python,编程入门,计算机科学' },
                    { id: 2, isbn: '978-7-115-42857-7', title: 'JavaScript高级程序设计', author: 'Nicholas C. Zakas', publisher: '人民邮电出版社', category: '编程', location: 'A区-1排-002', total_stock: 8, available_stock: 4, price: 129.0, description: 'JavaScript权威指南', keywords: 'JavaScript,前端,软件工程' },
                    { id: 3, isbn: '978-7-302-41580-7', title: '数据结构与算法分析', author: 'Mark Allen Weiss', publisher: '清华大学出版社', category: '计算机', location: 'B区-2排-001', total_stock: 6, available_stock: 2, price: 69.0, description: '数据结构与算法经典教材', keywords: '数据结构,算法,计算机科学' },
                    { id: 4, isbn: '978-7-111-40701-0', title: '算法导论', author: 'Thomas H. Cormen', publisher: '机械工业出版社', category: '计算机', location: 'B区-2排-002', total_stock: 5, available_stock: 2, price: 128.0, description: '算法领域的经典教材', keywords: '算法,计算机,数据结构' },
                    { id: 5, isbn: '978-7-115-37064-3', title: '深入浅出数据分析', author: 'Michael Milton', publisher: '人民邮电出版社', category: '数据分析', location: 'C区-3排-001', total_stock: 4, available_stock: 3, price: 59.0, description: '数据分析入门书籍', keywords: '数据分析,数据科学' },
                    { id: 6, isbn: '978-7-111-58165-5', title: '深度学习', author: 'Ian Goodfellow', publisher: '人民邮电出版社', category: '人工智能', location: 'C区-3排-002', total_stock: 3, available_stock: 1, price: 199.0, description: '深度学习领域的经典教材', keywords: '深度学习,AI,人工智能,数据科学' },
                    { id: 7, isbn: '978-7-302-50754-1', title: '机器学习', author: '周志华', publisher: '清华大学出版社', category: '人工智能', location: 'C区-3排-003', total_stock: 5, available_stock: 3, price: 89.0, description: '机器学习入门经典', keywords: '机器学习,AI,数据科学' },
                    { id: 8, isbn: '978-7-111-60022-4', title: 'Vue.js设计与实现', author: '霍春阳', publisher: '机械工业出版社', category: '编程', location: 'A区-1排-003', total_stock: 4, available_stock: 2, price: 119.0, description: 'Vue.js核心原理详解', keywords: 'Vue.js,前端,软件工程' },
                    { id: 9, isbn: '978-7-5086-5856-5', title: '经济学原理', author: '曼昆', publisher: '北京大学出版社', category: '经济学', location: 'D区-4排-001', total_stock: 8, available_stock: 6, price: 68.0, description: '经济学入门经典教材', keywords: '经济学' },
                    { id: 10, isbn: '978-7-04-045103-3', title: '高等数学', author: '同济大学', publisher: '高等教育出版社', category: '数学', location: 'E区-5排-001', total_stock: 15, available_stock: 10, price: 59.0, description: '高等数学经典教材', keywords: '高等数学,数学' },
                ],
                borrowRecords: [
                    { id: 1, user_id: 3, book_id: 1, book_title: 'Python编程：从入门到实践', borrow_date: daysAgo(10), due_date: daysAgo(-20), status: 'overdue', renew_count: 0, fine: 10 },
                    { id: 2, user_id: 3, book_id: 3, book_title: '数据结构与算法分析', borrow_date: daysAgo(20), due_date: daysAgo(-10), status: 'overdue', renew_count: 0, fine: 5 },
                    { id: 3, user_id: 4, book_id: 2, book_title: 'JavaScript高级程序设计', borrow_date: daysAgo(35), due_date: daysAgo(-5), status: 'overdue', renew_count: 0, fine: 2.5 },
                    { id: 4, user_id: 5, book_id: 5, book_title: '深入浅出数据分析', borrow_date: daysAgo(15), due_date: daysAgo(15), status: 'borrowed', renew_count: 0, fine: 0 },
                    { id: 5, user_id: 5, book_id: 7, book_title: '机器学习', borrow_date: daysAgo(60), return_date: daysAgo(40), due_date: daysAgo(30), status: 'returned', renew_count: 0, fine: 0 },
                ],
                secondhandBooks: [
                    { id: 1, user_id: 3, seller_name: '张三', title: 'Python编程：从入门到实践', author: 'Eric Matthes', isbn: '978-7-111-53551-1', condition: 'good', price: 45.0, description: '已阅读完毕，状态良好', status: 'available' },
                    { id: 2, user_id: 4, seller_name: '李四', title: 'JavaScript高级程序设计', author: 'Nicholas C. Zakas', isbn: '978-7-115-42857-7', condition: 'like_new', price: 80.0, description: '全新未拆封', status: 'available' },
                    { id: 3, user_id: 5, seller_name: '王五', title: '数据结构与算法分析', author: 'Mark Allen Weiss', isbn: '978-7-302-41580-7', condition: 'fair', price: 30.0, description: '有少量笔记', status: 'available' },
                ],
                secondhandTransactions: [],
                readingRecords: [
                    { id: 1, user_id: 3, book_id: 1, reading_date: daysAgo(5), minutes: 60 },
                    { id: 2, user_id: 3, book_id: 1, reading_date: daysAgo(3), minutes: 45 },
                    { id: 3, user_id: 3, book_id: 3, reading_date: daysAgo(4), minutes: 90 },
                    { id: 4, user_id: 4, book_id: 2, reading_date: daysAgo(10), minutes: 30 },
                    { id: 5, user_id: 5, book_id: 5, reading_date: daysAgo(7), minutes: 75 },
                    { id: 6, user_id: 5, book_id: 7, reading_date: daysAgo(50), minutes: 60 },
                ],
                stockAlerts: [
                    { id: 1, book_id: 4, book_title: '算法导论', threshold: 5, current_stock: 2, status: 'active' },
                    { id: 2, book_id: 6, book_title: '深度学习', threshold: 5, current_stock: 1, status: 'active' },
                ],
                bookRequests: [
                    { id: 1, user_id: 3, user_name: '张三', title: 'Python Cookbook', author: 'David Beazley', isbn: '978-7-111-47005-7', reason: '课程学习需要', status: 'pending' },
                    { id: 2, user_id: 4, user_name: '李四', title: '设计模式', author: 'Erich Gamma', isbn: '978-7-111-07554-7', reason: '毕业设计参考', status: 'approved' },
                ],
                notifications: [
                    { id: 1, user_id: 4, title: '图书逾期提醒', content: '您借阅的《JavaScript高级程序设计》已逾期5天，请尽快归还！', type: 'overdue', read: false, created_at: daysAgo(1) + 'T10:00:00' },
                    { id: 2, user_id: 3, title: '借阅成功', content: '您已成功借阅《Python编程：从入门到实践》，请于到期前归还或续借。', type: 'system', read: false, created_at: daysAgo(9) + 'T14:30:00' },
                ],
                recommendations: [
                    { id: 1, user_id: 3, book_id: 6, book_title: '深度学习', score: 50, reason: '专业匹配；关键词匹配' },
                    { id: 2, user_id: 3, book_id: 4, book_title: '算法导论', score: 40, reason: '专业匹配' },
                    { id: 3, user_id: 4, book_id: 8, book_title: 'Vue.js设计与实现', score: 50, reason: '关键词匹配' },
                ],
            };
        },
        saveData() {
            localStorage.setItem('libraryData', JSON.stringify({
                books: this.books,
                borrowRecords: this.borrowRecords,
                secondhandBooks: this.secondhandBooks,
                secondhandTransactions: this.secondhandTransactions || [],
                readingRecords: this.readingRecords || [],
                stockAlerts: this.stockAlerts,
                bookRequests: this.bookRequests,
                notifications: this.notifications,
                recommendations: this.recommendations,
                users: this.users,
            }));
        },
        login() {
            const user = this.users.find(u => u.username === this.loginForm.username && u.password === this.loginForm.password);
            if (user) {
                this.currentUser = user;
                this.isLoggedIn = true;
                localStorage.setItem('currentUser', JSON.stringify(user));
                this.loadDashboard();
            } else {
                alert('用户名或密码错误');
            }
        },
        register() {
            if (this.users.find(u => u.username === this.registerForm.username)) {
                alert('用户名已存在');
                return;
            }
            if (this.users.find(u => u.student_id === this.registerForm.student_id)) {
                alert('学号已被注册');
                return;
            }
            const newUser = {
                id: this.users.length + 1,
                username: this.registerForm.username,
                password: this.registerForm.password,
                real_name: this.registerForm.real_name,
                student_id: this.registerForm.student_id,
                major: this.registerForm.major,
                role: 'student',
                total_reading_minutes: 0
            };
            this.users.push(newUser);
            this.saveData();
            alert('注册成功，请登录');
            this.loginTab = 'login';
        },
        logout() {
            localStorage.removeItem('currentUser');
            this.isLoggedIn = false;
            this.currentUser = {};
        },
        loadDashboard() {
            this.loadDashboardStats();
            this.loadTopBooks();
            this.loadMyBorrows();
            this.loadNotifications();
        },
        loadDashboardStats() {
            const borrowed = this.borrowRecords.filter(r => ['borrowed', 'overdue', 'renewed'].includes(r.status)).length;
            const overdue = this.borrowRecords.filter(r => r.status === 'overdue').length;
            this.dashboardStats = {
                total_books: this.books.length,
                total_users: this.users.filter(u => u.role === 'student').length,
                total_borrowed: borrowed,
                overdue_count: overdue,
                active_alerts: this.stockAlerts.filter(a => a.status === 'active').length
            };
        },
        loadTopBooks() {
            const counts = {};
            this.borrowRecords.forEach(r => {
                counts[r.book_id] = (counts[r.book_id] || 0) + 1;
            });
            this.topBooks = Object.entries(counts)
                .map(([id, count]) => ({
                    id: parseInt(id),
                    title: this.books.find(b => b.id === parseInt(id))?.title || '未知',
                    borrow_count: count
                }))
                .sort((a, b) => b.borrow_count - a.borrow_count)
                .slice(0, 10);
        },
        loadMyBorrows() {
            this.myBorrows = this.borrowRecords
                .filter(r => r.user_id === this.currentUser.id && r.status !== 'returned')
                .sort((a, b) => new Date(b.borrow_date) - new Date(a.borrow_date));
        },
        loadNotifications() {
            this.notifications = this.notifications || [];
            this.unreadCount = this.notifications.filter(n => n.user_id === this.currentUser.id && !n.read).length;
        },
        markAllRead() {
            this.notifications.forEach(n => {
                if (n.user_id === this.currentUser.id) {
                    n.read = true;
                }
            });
            this.unreadCount = 0;
            this.saveData();
        },
        searchBooks() {
            this.filteredBooks = this.books.filter(book => {
                const matchKeyword = !this.searchKeyword || 
                    book.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                    book.author.toLowerCase().includes(this.searchKeyword.toLowerCase());
                const matchCategory = !this.searchCategory || book.category === this.searchCategory;
                return matchKeyword && matchCategory;
            });
        },
        viewBook(book) {
            alert(`书名: ${book.title}\n作者: ${book.author}\n出版社: ${book.publisher}\n简介: ${book.description}`);
        },
        editBook(book) {
            this.editBookData = book;
            this.bookForm = { ...book };
            $('#showAddBook').modal('show');
        },
        saveBook() {
            if (this.editBookData) {
                const index = this.books.findIndex(b => b.id === this.editBookData.id);
                if (index !== -1) {
                    this.books[index] = { ...this.bookForm };
                }
            } else {
                const newBook = { ...this.bookForm, id: this.books.length + 1 };
                this.books.push(newBook);
                this.categories = [...new Set(this.books.map(b => b.category).filter(Boolean))];
            }
            $('#showAddBook').modal('hide');
            this.bookForm = { isbn: '', title: '', author: '', publisher: '', category: '', location: '', total_stock: 0, available_stock: 0, price: 0, description: '', keywords: '' };
            this.editBookData = null;
            this.saveData();
            this.loadDashboardStats();
            alert('保存成功');
        },
        deleteBook(id) {
            if (!confirm('确定删除这本书吗？')) return;
            this.books = this.books.filter(b => b.id !== id);
            this.saveData();
            alert('删除成功');
        },
        borrowBook(bookId) {
            const book = this.books.find(b => b.id === bookId);
            if (!book) {
                alert('图书不存在');
                return;
            }
            if (book.available_stock <= 0) {
                alert('库存不足');
                return;
            }
            const activeBorrows = this.borrowRecords.filter(r => 
                r.user_id === this.currentUser.id && 
                ['borrowed', 'overdue', 'renewed'].includes(r.status)
            ).length;
            if (activeBorrows >= 5) {
                alert('已达到最大借阅数量(5本)');
                return;
            }
            const today = new Date().toISOString().split('T')[0];
            const dueDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            const newRecord = {
                id: this.borrowRecords.length + 1,
                user_id: this.currentUser.id,
                book_id: bookId,
                book_title: book.title,
                borrow_date: today,
                due_date: dueDate,
                status: 'borrowed',
                renew_count: 0,
                fine: 0
            };
            this.borrowRecords.push(newRecord);
            book.available_stock--;
            this.saveData();
            this.loadDashboard();
            alert('借阅成功');
        },
        renewBook(recordId) {
            const record = this.borrowRecords.find(r => r.id === recordId);
            if (!record) {
                alert('借阅记录不存在');
                return;
            }
            if (record.renew_count >= this.maxRenewCount) {
                alert('已达到最大续借次数');
                return;
            }
            const dueDate = new Date(new Date(record.due_date).getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            record.due_date = dueDate;
            record.renew_count++;
            record.status = 'renewed';
            this.saveData();
            this.loadMyBorrows();
            alert('续借成功');
        },
        returnBook(recordId) {
            const record = this.borrowRecords.find(r => r.id === recordId);
            if (!record) {
                alert('借阅记录不存在');
                return;
            }
            const today = new Date().toISOString().split('T')[0];
            record.return_date = today;
            record.status = 'returned';
            const book = this.books.find(b => b.id === record.book_id);
            if (book) {
                book.available_stock++;
            }
            this.saveData();
            this.loadDashboard();
            alert('归还成功');
        },
        scanBorrow() {
            if (!this.scanData) {
                alert('请输入二维码内容');
                return;
            }
            const match = this.scanData.match(/BOOK:(\d+)/);
            if (!match) {
                alert('无效的二维码格式');
                return;
            }
            const bookId = parseInt(match[1]);
            this.borrowBook(bookId);
            this.scanData = '';
        },
        scanReturn() {
            if (!this.scanData) {
                alert('请输入二维码内容');
                return;
            }
            const match = this.scanData.match(/BOOK:(\d+)/);
            if (!match) {
                alert('无效的二维码格式');
                return;
            }
            const bookId = parseInt(match[1]);
            const record = this.borrowRecords.find(r => 
                r.book_id === bookId && 
                r.user_id === this.currentUser.id && 
                ['borrowed', 'overdue', 'renewed'].includes(r.status)
            );
            if (!record) {
                alert('未找到借阅记录');
                return;
            }
            this.returnBook(record.id);
            this.scanData = '';
        },
        loadRecommendations() {
            this.recommendations = this.recommendations.filter(r => r.user_id === this.currentUser.id);
        },
        generateRecommendations() {
            const user = this.currentUser;
            const results = [];
            this.books.forEach(book => {
                let score = 0;
                const reasons = [];
                if (user.major && book.category && user.major.includes(book.category)) {
                    score += 30;
                    reasons.push('专业匹配');
                }
                if (book.keywords && user.major && book.keywords.includes(user.major)) {
                    score += 20;
                    reasons.push('关键词匹配');
                }
                const userBorrows = this.borrowRecords.filter(r => r.user_id === user.id && r.book_id === book.id).length;
                if (userBorrows > 0) {
                    score += 15;
                    reasons.push('曾借阅过');
                }
                if (book.available_stock > 0) {
                    score += 10;
                }
                if (score > 0) {
                    results.push({ book_id: book.id, book_title: book.title, score, reason: reasons.join('；') });
                }
            });
            results.sort((a, b) => b.score - a.score);
            this.recommendations = results.slice(0, 10).map((r, i) => ({ id: this.recommendations.length + 1 + i, user_id: user.id, ...r }));
            this.saveData();
            alert('推荐生成成功');
        },
        loadSecondhandBooks() {
            this.secondhandBooks = this.secondhandBooks || [];
        },
        searchSecondhand() {
            this.filteredSecondhandBooks = this.secondhandBooks.filter(book => {
                return !this.secondhandKeyword || 
                    book.title.toLowerCase().includes(this.secondhandKeyword.toLowerCase());
            });
        },
        saveSecondhand() {
            const newBook = {
                id: this.secondhandBooks.length + 1,
                user_id: this.currentUser.id,
                seller_name: this.currentUser.real_name,
                ...this.secondhandForm,
                status: 'available'
            };
            this.secondhandBooks.push(newBook);
            $('#showAddSecondhand').modal('hide');
            this.secondhandForm = { title: '', author: '', isbn: '', condition: 'good', price: 0, description: '' };
            this.saveData();
            alert('发布成功');
        },
        buySecondhand(bookId) {
            const book = this.secondhandBooks.find(b => b.id === bookId);
            if (!book) {
                alert('图书不存在');
                return;
            }
            book.status = 'reserved';
            const today = new Date().toISOString().split('T')[0];
            const transaction = {
                id: (this.secondhandTransactions?.length || 0) + 1,
                book_id: bookId,
                book_title: book.title,
                buyer_id: this.currentUser.id,
                buyer_name: this.currentUser.real_name,
                seller_id: book.user_id,
                seller_name: book.seller_name,
                transaction_date: today,
                status: 'pending'
            };
            if (!this.secondhandTransactions) this.secondhandTransactions = [];
            this.secondhandTransactions.push(transaction);
            this.saveData();
            alert('交易申请已提交');
        },
        loadTransactions() {
            this.myTransactions = (this.secondhandTransactions || []).filter(t => 
                t.buyer_id === this.currentUser.id || t.seller_id === this.currentUser.id
            );
        },
        completeTransaction(id) {
            const transaction = (this.secondhandTransactions || []).find(t => t.id === id);
            if (!transaction) {
                alert('交易记录不存在');
                return;
            }
            transaction.status = 'completed';
            const book = this.secondhandBooks.find(b => b.id === transaction.book_id);
            if (book) {
                book.status = 'sold';
            }
            this.saveData();
            this.loadTransactions();
            alert('交易完成');
        },
        loadReadingStats() {
            const userRecords = (this.readingRecords || []).filter(r => r.user_id === this.currentUser.id);
            const totalMinutes = userRecords.reduce((sum, r) => sum + r.minutes, 0);
            const monthlyMap = {};
            userRecords.forEach(r => {
                const month = r.reading_date.substring(0, 7);
                monthlyMap[month] = (monthlyMap[month] || 0) + r.minutes;
            });
            this.readingStats = {
                total_minutes: totalMinutes,
                monthly_stats: Object.entries(monthlyMap).map(([month, minutes]) => ({ month, minutes }))
            };
            this.drawReadingChart();
        },
        drawReadingChart() {
            const ctx = document.getElementById('readingChart');
            if (!ctx || this.readingStats.monthly_stats.length === 0) return;
            
            if (window.readingChart) {
                window.readingChart.destroy();
            }
            
            const labels = this.readingStats.monthly_stats.map(s => s.month);
            const data = this.readingStats.monthly_stats.map(s => s.minutes);
            
            window.readingChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '阅读时长(分钟)',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },
        saveReading() {
            if (this.readingForm.minutes <= 0) {
                alert('阅读时长必须大于0');
                return;
            }
            const today = new Date().toISOString().split('T')[0];
            const existing = (this.readingRecords || []).find(r => 
                r.user_id === this.currentUser.id && 
                r.book_id === this.readingForm.book_id && 
                r.reading_date === today
            );
            if (existing) {
                existing.minutes += this.readingForm.minutes;
            } else {
                if (!this.readingRecords) this.readingRecords = [];
                this.readingRecords.push({
                    id: this.readingRecords.length + 1,
                    user_id: this.currentUser.id,
                    book_id: this.readingForm.book_id,
                    reading_date: today,
                    minutes: this.readingForm.minutes
                });
            }
            const user = this.users.find(u => u.id === this.currentUser.id);
            if (user) {
                user.total_reading_minutes = (user.total_reading_minutes || 0) + this.readingForm.minutes;
            }
            this.currentUser.total_reading_minutes = (this.currentUser.total_reading_minutes || 0) + this.readingForm.minutes;
            localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
            $('#showAddReading').modal('hide');
            this.readingForm = { book_id: '', minutes: 0 };
            this.saveData();
            this.loadReadingStats();
            alert('添加成功');
        },
        loadClassStats() {
            const stats = {};
            this.users.filter(u => u.role === 'student' && u.major).forEach(user => {
                if (!stats[user.major]) {
                    stats[user.major] = { total_users: 0, total_reading_minutes: 0, total_borrows: 0 };
                }
                stats[user.major].total_users++;
                stats[user.major].total_reading_minutes += user.total_reading_minutes || 0;
            });
            this.borrowRecords.forEach(record => {
                const user = this.users.find(u => u.id === record.user_id);
                if (user && user.major) {
                    stats[user.major] = stats[user.major] || { total_users: 0, total_reading_minutes: 0, total_borrows: 0 };
                    stats[user.major].total_borrows++;
                }
            });
            this.classStats = Object.entries(stats).map(([major, data]) => ({ major, ...data }));
        },
        loadStockAlerts() {
            this.stockAlerts = this.stockAlerts || [];
        },
        resolveAlert(id) {
            const alertItem = this.stockAlerts.find(a => a.id === id);
            if (!alertItem) {
                alert('预警不存在');
                return;
            }
            alertItem.status = 'resolved';
            this.saveData();
            alert('已处理');
        },
        loadBookRequests() {
            this.bookRequests = this.bookRequests || [];
        },
        saveRequest() {
            const newRequest = {
                id: this.bookRequests.length + 1,
                user_id: this.currentUser.id,
                user_name: this.currentUser.real_name,
                ...this.requestForm,
                status: 'pending'
            };
            this.bookRequests.push(newRequest);
            $('#showAddRequest').modal('hide');
            this.requestForm = { title: '', author: '', isbn: '', reason: '' };
            this.saveData();
            alert('申请提交成功');
        },
        updateRequest(id, status) {
            const req = this.bookRequests.find(r => r.id === id);
            if (!req) {
                alert('申请不存在');
                return;
            }
            req.status = status;
            this.saveData();
            alert('状态已更新');
        },
        formatDate(dateStr) {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        },
        formatDateTime(dateStr) {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        },
        getStatusClass(status) {
            const classes = {
                borrowed: 'badge-primary',
                returned: 'badge-success',
                overdue: 'badge-danger',
                renewed: 'badge-warning'
            };
            return classes[status] || 'badge-secondary';
        },
        getStatusText(status) {
            const texts = {
                borrowed: '借阅中',
                returned: '已归还',
                overdue: '已逾期',
                renewed: '已续借'
            };
            return texts[status] || status;
        },
        getConditionClass(condition) {
            const classes = {
                like_new: 'badge-success',
                good: 'badge-primary',
                fair: 'badge-warning',
                poor: 'badge-danger'
            };
            return classes[condition] || 'badge-secondary';
        },
        getConditionText(condition) {
            const texts = {
                like_new: '全新',
                good: '良好',
                fair: '一般',
                poor: '较差'
            };
            return texts[condition] || condition;
        },
        getTransactionStatusClass(status) {
            const classes = {
                pending: 'badge-warning',
                completed: 'badge-success',
                cancelled: 'badge-danger'
            };
            return classes[status] || 'badge-secondary';
        },
        getTransactionStatusText(status) {
            const texts = {
                pending: '待确认',
                completed: '已完成',
                cancelled: '已取消'
            };
            return texts[status] || status;
        },
        getRequestStatusClass(status) {
            const classes = {
                pending: 'badge-warning',
                approved: 'badge-primary',
                rejected: 'badge-danger',
                purchased: 'badge-success'
            };
            return classes[status] || 'badge-secondary';
        },
        getRequestStatusText(status) {
            const texts = {
                pending: '待审核',
                approved: '已批准',
                rejected: '已拒绝',
                purchased: '已采购'
            };
            return texts[status] || status;
        },
        loadPageData() {
            switch (this.currentPage) {
                case 'dashboard':
                    this.loadDashboard();
                    break;
                case 'books':
                    break;
                case 'borrow':
                    this.loadMyBorrows();
                    break;
                case 'recommend':
                    this.loadRecommendations();
                    break;
                case 'secondhand':
                    this.loadTransactions();
                    break;
                case 'reading':
                    this.loadReadingStats();
                    break;
                case 'stats':
                    this.loadClassStats();
                    break;
                case 'alerts':
                    break;
                case 'requests':
                    break;
            }
        }
    },
    watch: {
        currentPage() {
            this.loadPageData();
        }
    }
});