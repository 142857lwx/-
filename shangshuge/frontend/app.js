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
        overdueRecords: [],
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
        secondhandForm: { title: '', author: '', isbn: '', condition: 'good', price: 0, description: '', contact: '' },
        
        showAddReading: false,
        readingForm: { book_id: '', minutes: 0 },
        
        showAddRequest: false,
        requestForm: { title: '', author: '', isbn: '', reason: '' },
        
        scanData: '',
        
        // 分页相关
        currentBookPage: 1,
        booksPerPage: 10,
        
        // 查看二手图书详情
        showSecondhandDetail: false,
        selectedSecondhandBook: null
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
            let result = this.books.filter(book => {
                const matchKeyword = !this.searchKeyword || 
                    book.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                    book.author.toLowerCase().includes(this.searchKeyword.toLowerCase());
                const matchCategory = !this.searchCategory || book.category === this.searchCategory;
                return matchKeyword && matchCategory;
            });
            return result;
        },
        paginatedBooks() {
            const start = (this.currentBookPage - 1) * this.booksPerPage;
            const end = start + this.booksPerPage;
            return this.filteredBooks.slice(start, end);
        },
        totalBookPages() {
            return Math.ceil(this.filteredBooks.length / this.booksPerPage);
        },
        visibleBorrowRecords() {
            if (this.currentUser.role === 'admin' || this.currentUser.role === 'librarian') {
                return this.borrowRecords;
            }
            return this.borrowRecords.filter(r => r.user_id === this.currentUser.id);
        },
        visibleOverdueRecords() {
            if (this.currentUser.role === 'admin' || this.currentUser.role === 'librarian') {
                return this.borrowRecords.filter(r => r.status === 'overdue');
            }
            return this.borrowRecords.filter(r => r.user_id === this.currentUser.id && r.status === 'overdue');
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
        },
        allSecondhandBooksForAdmin() {
            return this.secondhandBooks;
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
            
            const generateBooks = () => {
                const categories = ['编程', '计算机', '数据分析', '人工智能', '经济学', '数学', '文学', '历史', '哲学', '心理学'];
                const locations = [];
                const floors = ['一楼', '二楼', '三楼', '四楼'];
                const libraries = ['01图书馆', '02图书馆', '03图书馆', '04图书馆'];
                const shelves = ['A1图书架', 'A2图书架', 'B1图书架', 'B2图书架', 'C1图书架', 'C2图书架', 'D1图书架', 'D2图书架'];
                
                for (let f = 0; f < floors.length; f++) {
                    for (let l = 0; l < libraries.length; l++) {
                        for (let s = 0; s < shelves.length; s++) {
                            for (let r = 1; r <= 5; r++) {
                                for (let n = 1; n <= 5; n++) {
                                    locations.push(`${floors[f]}${libraries[l]}-${shelves[s]}-${r}排${String(n).padStart(3, '0')}`);
                                }
                            }
                        }
                    }
                }
                
                const books = [];
                
                const bookData = [
                    { title: 'Python编程：从入门到实践', author: 'Eric Matthes', publisher: '人民邮电出版社', category: '编程', keywords: 'Python,编程入门,计算机科学' },
                    { title: 'JavaScript高级程序设计', author: 'Nicholas C. Zakas', publisher: '人民邮电出版社', category: '编程', keywords: 'JavaScript,前端,软件工程' },
                    { title: '数据结构与算法分析', author: 'Mark Allen Weiss', publisher: '清华大学出版社', category: '计算机', keywords: '数据结构,算法,计算机科学' },
                    { title: '算法导论', author: 'Thomas H. Cormen', publisher: '机械工业出版社', category: '计算机', keywords: '算法,计算机,数据结构' },
                    { title: '深入浅出数据分析', author: 'Michael Milton', publisher: '人民邮电出版社', category: '数据分析', keywords: '数据分析,数据科学' },
                    { title: '深度学习', author: 'Ian Goodfellow', publisher: '人民邮电出版社', category: '人工智能', keywords: '深度学习,AI,人工智能,数据科学' },
                    { title: '机器学习', author: '周志华', publisher: '清华大学出版社', category: '人工智能', keywords: '机器学习,AI,数据科学' },
                    { title: 'Vue.js设计与实现', author: '霍春阳', publisher: '机械工业出版社', category: '编程', keywords: 'Vue.js,前端,软件工程' },
                    { title: '经济学原理', author: '曼昆', publisher: '北京大学出版社', category: '经济学', keywords: '经济学' },
                    { title: '高等数学', author: '同济大学', publisher: '高等教育出版社', category: '数学', keywords: '高等数学,数学' },
                    { title: '红楼梦', author: '曹雪芹', publisher: '人民文学出版社', category: '文学', keywords: '古典文学,小说' },
                    { title: '三国演义', author: '罗贯中', publisher: '人民文学出版社', category: '文学', keywords: '古典文学,历史小说' },
                    { title: '水浒传', author: '施耐庵', publisher: '人民文学出版社', category: '文学', keywords: '古典文学,小说' },
                    { title: '西游记', author: '吴承恩', publisher: '人民文学出版社', category: '文学', keywords: '古典文学,神话' },
                    { title: '明朝那些事儿', author: '当年明月', publisher: '浙江人民出版社', category: '历史', keywords: '中国历史,明朝' },
                    { title: '万历十五年', author: '黄仁宇', publisher: '中华书局', category: '历史', keywords: '中国历史,明朝' },
                    { title: '苏菲的世界', author: '乔斯坦·贾德', publisher: '作家出版社', category: '哲学', keywords: '哲学入门,西方哲学' },
                    { title: '沉思录', author: '马可·奥勒留', publisher: '中央编译出版社', category: '哲学', keywords: '哲学,斯多葛学派' },
                    { title: '社会心理学', author: '戴维·迈尔斯', publisher: '人民邮电出版社', category: '心理学', keywords: '心理学,社会心理学' },
                    { title: '认知心理学', author: '索尔所', publisher: '人民邮电出版社', category: '心理学', keywords: '心理学,认知' },
                    { title: 'Java编程思想', author: 'Bruce Eckel', publisher: '机械工业出版社', category: '编程', keywords: 'Java,编程' },
                    { title: 'C++ Primer', author: 'Stanley B. Lippman', publisher: '人民邮电出版社', category: '编程', keywords: 'C++,编程' },
                    { title: '操作系统概念', author: 'Abraham Silberschatz', publisher: '高等教育出版社', category: '计算机', keywords: '操作系统,计算机' },
                    { title: '计算机网络', author: '谢希仁', publisher: '电子工业出版社', category: '计算机', keywords: '计算机网络,网络协议' },
                    { title: '数据库系统概念', author: 'Abraham Silberschatz', publisher: '机械工业出版社', category: '计算机', keywords: '数据库,SQL' },
                    { title: '统计学导论', author: 'David Freedman', publisher: '机械工业出版社', category: '数据分析', keywords: '统计学,数据分析' },
                    { title: '数据挖掘导论', author: 'Jiawei Han', publisher: '人民邮电出版社', category: '数据分析', keywords: '数据挖掘,机器学习' },
                    { title: '人工智能导论', author: 'Russell', publisher: '清华大学出版社', category: '人工智能', keywords: '人工智能,AI' },
                    { title: '自然语言处理入门', author: '何晗', publisher: '人民邮电出版社', category: '人工智能', keywords: 'NLP,自然语言处理' },
                    { title: '计量经济学', author: '伍德里奇', publisher: '中国人民大学出版社', category: '经济学', keywords: '经济学,计量' },
                    { title: '线性代数', author: '同济大学', publisher: '高等教育出版社', category: '数学', keywords: '线性代数,数学' },
                    { title: '概率论与数理统计', author: '盛骤', publisher: '高等教育出版社', category: '数学', keywords: '概率论,统计学' },
                    { title: '百年孤独', author: '加西亚·马尔克斯', publisher: '南海出版公司', category: '文学', keywords: '魔幻现实主义,小说' },
                    { title: '1984', author: '乔治·奥威尔', publisher: '北京十月文艺出版社', category: '文学', keywords: '反乌托邦,小说' },
                    { title: '活着', author: '余华', publisher: '作家出版社', category: '文学', keywords: '当代文学,小说' },
                    { title: '围城', author: '钱钟书', publisher: '人民文学出版社', category: '文学', keywords: '现代文学,小说' },
                    { title: '全球通史', author: '斯塔夫里阿诺斯', publisher: '北京大学出版社', category: '历史', keywords: '世界历史,通史' },
                    { title: '中国通史', author: '吕思勉', publisher: '中华书局', category: '历史', keywords: '中国历史,通史' },
                    { title: '西方哲学史', author: '罗素', publisher: '商务印书馆', category: '哲学', keywords: '西方哲学,哲学史' },
                    { title: '中国哲学史', author: '冯友兰', publisher: '华东师范大学出版社', category: '哲学', keywords: '中国哲学,哲学史' },
                    { title: '发展心理学', author: 'David R. Shaffer', publisher: '中国轻工业出版社', category: '心理学', keywords: '心理学,发展' },
                    { title: '变态心理学', author: 'Durand', publisher: '中国轻工业出版社', category: '心理学', keywords: '心理学,变态' },
                    { title: 'React设计模式', author: 'Michele Bertoli', publisher: '人民邮电出版社', category: '编程', keywords: 'React,前端' },
                    { title: 'Node.js实战', author: 'Alex Young', publisher: '人民邮电出版社', category: '编程', keywords: 'Node.js,后端' },
                    { title: 'Go语言实战', author: 'William Kennedy', publisher: '人民邮电出版社', category: '编程', keywords: 'Go,编程' },
                    { title: 'Rust编程入门', author: 'Steve Klabnik', publisher: '人民邮电出版社', category: '编程', keywords: 'Rust,编程' },
                    { title: '编译原理', author: 'Alfred Aho', publisher: '机械工业出版社', category: '计算机', keywords: '编译原理,编译器' },
                    { title: '软件工程导论', author: '张海藩', publisher: '清华大学出版社', category: '计算机', keywords: '软件工程' },
                    { title: '人机交互', author: 'Alan Dix', publisher: '机械工业出版社', category: '计算机', keywords: '人机交互,HCI' },
                    { title: '信息安全', author: 'William Stallings', publisher: '电子工业出版社', category: '计算机', keywords: '信息安全,网络安全' },
                    { title: '大数据技术原理与应用', author: '林子雨', publisher: '人民邮电出版社', category: '数据分析', keywords: '大数据,Hadoop' },
                    { title: '云计算导论', author: 'Thomas Erl', publisher: '机械工业出版社', category: '数据分析', keywords: '云计算,云服务' },
                    { title: '强化学习', author: 'Richard Sutton', publisher: '机械工业出版社', category: '人工智能', keywords: '强化学习,AI' },
                    { title: '计算机视觉', author: 'Szeliski', publisher: ' Springer', category: '人工智能', keywords: '计算机视觉,CV' },
                    { title: '宏观经济学', author: '曼昆', publisher: '中国人民大学出版社', category: '经济学', keywords: '经济学,宏观' },
                    { title: '微观经济学', author: '平狄克', publisher: '中国人民大学出版社', category: '经济学', keywords: '经济学,微观' },
                    { title: '离散数学', author: '屈婉玲', publisher: '高等教育出版社', category: '数学', keywords: '离散数学,数学' },
                    { title: '复变函数', author: '钟玉泉', publisher: '高等教育出版社', category: '数学', keywords: '复变函数,数学' },
                    { title: '平凡的世界', author: '路遥', publisher: '人民文学出版社', category: '文学', keywords: '当代文学,小说' },
                    { title: '骆驼祥子', author: '老舍', publisher: '人民文学出版社', category: '文学', keywords: '现代文学,小说' },
                    { title: '茶馆', author: '老舍', publisher: '人民文学出版社', category: '文学', keywords: '戏剧,文学' },
                    { title: '雷雨', author: '曹禺', publisher: '人民文学出版社', category: '文学', keywords: '戏剧,文学' },
                    { title: '罗马人的故事', author: '盐野七生', publisher: '中信出版社', category: '历史', keywords: '古罗马,历史' },
                    { title: '德川家康', author: '山冈庄八', publisher: '南海出版公司', category: '历史', keywords: '日本历史,战国' },
                    { title: '理想国', author: '柏拉图', publisher: '商务印书馆', category: '哲学', keywords: '古希腊哲学,柏拉图' },
                    { title: '尼各马可伦理学', author: '亚里士多德', publisher: '商务印书馆', category: '哲学', keywords: '古希腊哲学,伦理学' },
                    { title: '精神分析引论', author: '弗洛伊德', publisher: '商务印书馆', category: '心理学', keywords: '精神分析,心理学' },
                    { title: '梦的解析', author: '弗洛伊德', publisher: '商务印书馆', category: '心理学', keywords: '精神分析,梦' },
                    { title: 'TypeScript实战', author: 'Basarat Ali Syed', publisher: '人民邮电出版社', category: '编程', keywords: 'TypeScript,前端' },
                    { title: 'GraphQL实战', author: 'Sam Newman', publisher: '人民邮电出版社', category: '编程', keywords: 'GraphQL,API' },
                    { title: 'Docker实战', author: 'James Turnbull', publisher: '人民邮电出版社', category: '编程', keywords: 'Docker,容器' },
                    { title: 'Kubernetes实战', author: 'Marko Lukša', publisher: '人民邮电出版社', category: '编程', keywords: 'Kubernetes,容器编排' },
                    { title: '微服务设计', author: 'Sam Newman', publisher: '人民邮电出版社', category: '计算机', keywords: '微服务,架构' },
                    { title: '架构师修炼之道', author: 'Michael Keeling', publisher: '机械工业出版社', category: '计算机', keywords: '架构,设计' },
                    { title: '数据仓库', author: 'William Inmon', publisher: '机械工业出版社', category: '数据分析', keywords: '数据仓库,BI' },
                    { title: '数据可视化', author: 'Colin Ware', publisher: '电子工业出版社', category: '数据分析', keywords: '数据可视化,图表' },
                    { title: 'NLP入门实战', author: '何晗', publisher: '电子工业出版社', category: '人工智能', keywords: 'NLP,自然语言处理' },
                    { title: '强化学习实战', author: 'Tao Wang', publisher: '电子工业出版社', category: '人工智能', keywords: '强化学习,实战' },
                    { title: '软件工程：实践者的研究方法', author: 'Roger Pressman', publisher: '机械工业出版社', category: '计算机', keywords: '软件工程,方法论' },
                    { title: '人月神话', author: 'Frederick Brooks', publisher: '清华大学出版社', category: '计算机', keywords: '软件工程,经典' },
                    { title: '代码大全', author: 'Steve McConnell', publisher: '电子工业出版社', category: '编程', keywords: '编程,最佳实践' },
                    { title: '设计模式：可复用面向对象软件的基础', author: 'Erich Gamma', publisher: '机械工业出版社', category: '编程', keywords: '设计模式,面向对象' },
                    { title: '重构：改善既有代码的设计', author: 'Martin Fowler', publisher: '人民邮电出版社', category: '编程', keywords: '重构,代码优化' },
                    { title: '代码整洁之道', author: 'Robert Martin', publisher: '人民邮电出版社', category: '编程', keywords: '代码规范,编程' },
                    { title: '程序员修炼之道', author: 'Andrew Hunt', publisher: '电子工业出版社', category: '编程', keywords: '程序员,职业发展' },
                    { title: '计算机程序设计艺术', author: 'Donald Knuth', publisher: '机械工业出版社', category: '计算机', keywords: '算法,编程艺术' },
                    { title: '深入浅出设计模式', author: 'Eric Freeman', publisher: '东南大学出版社', category: '编程', keywords: '设计模式,入门' },
                    { title: 'Head First设计模式', author: 'Eric Freeman', publisher: '中国电力出版社', category: '编程', keywords: '设计模式,入门' },
                ];
                
                for (let i = 0; i < bookData.length; i++) {
                    const book = bookData[i];
                    const copies = Math.floor(Math.random() * 5) + 3;
                    books.push({
                        id: i + 1,
                        isbn: `978-7-${String(Math.floor(Math.random() * 9000 + 1000)).padStart(4, '0')}-${String(Math.floor(Math.random() * 900) + 100)}`,
                        title: book.title,
                        author: book.author,
                        publisher: book.publisher,
                        category: book.category,
                        location: locations[i % locations.length],
                        total_stock: copies,
                        available_stock: copies,
                        price: Math.floor(Math.random() * 150) + 30,
                        description: `这是一本关于${book.keywords.split(',')[0]}的优秀书籍`,
                        keywords: book.keywords
                    });
                }
                return books;
            };
            
            const generateUsers = () => {
                const majors = ['计算机科学', '软件工程', '数据科学', '人工智能', '经济学', '数学', '心理学', '历史学'];
                const users = [
                    { id: 1, username: 'admin', password: 'password', real_name: '管理员', role: 'admin', student_id: 'ADMIN001', email: 'admin@library.edu', phone: '13800000000', total_reading_minutes: 0 },
                    { id: 2, username: 'librarian', password: 'password', real_name: '图书管理员', role: 'librarian', student_id: 'LIB001', email: 'librarian@library.edu', phone: '13800000001', total_reading_minutes: 0 },
                ];
                
                const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '陈十三', '刘十四', '杨十五', '黄十六', '周十七', '吴十八', '郑十九', '王二十', '陈二十一', '刘二十二'];
                
                for (let i = 0; i < 18; i++) {
                    users.push({
                        id: i + 3,
                        username: `student${i + 1}`,
                        password: 'password',
                        real_name: names[i],
                        role: 'student',
                        major: majors[i % majors.length],
                        student_id: `2021${String(i + 1).padStart(3, '0')}`,
                        email: `student${i + 1}@library.edu`,
                        phone: `138000000${String(i + 2).padStart(2, '0')}`,
                        total_reading_minutes: Math.floor(Math.random() * 500) + 50
                    });
                }
                return users;
            };
            
            const generateBorrowRecords = (books, users) => {
                const records = [];
                let recordId = 1;
                
                const studentUsers = users.filter(u => u.role === 'student');
                
                for (let i = 0; i < 40; i++) {
                    const user = studentUsers[i % studentUsers.length];
                    const book = books[Math.floor(Math.random() * books.length)];
                    const borrowDays = Math.floor(Math.random() * 60);
                    const isOverdue = i < 10;
                    const dueDays = isOverdue ? -Math.floor(Math.random() * 30) - 1 : Math.floor(Math.random() * 30);
                    const isReturned = Math.random() > 0.7;
                    
                    records.push({
                        id: recordId++,
                        user_id: user.id,
                        book_id: book.id,
                        book_title: book.title,
                        borrow_date: daysAgo(borrowDays),
                        due_date: daysAgo(dueDays),
                        return_date: isReturned ? daysAgo(Math.floor(Math.random() * borrowDays)) : null,
                        status: isReturned ? 'returned' : (isOverdue ? 'overdue' : 'borrowed'),
                        renew_count: Math.floor(Math.random() * 2),
                        fine: isOverdue ? Math.floor(Math.random() * 20) + 1 : 0
                    });
                }
                return records;
            };
            
            const books = generateBooks();
            const users = generateUsers();
            const borrowRecords = generateBorrowRecords(books, users);
            
            borrowRecords.forEach(record => {
                if (record.status !== 'returned') {
                    const book = books.find(b => b.id === record.book_id);
                    if (book) {
                        book.available_stock = Math.max(0, book.available_stock - 1);
                    }
                }
            });
            
            return {
                users: users,
                books: books,
                borrowRecords: borrowRecords,
                secondhandBooks: [
                    { id: 1, user_id: 3, seller_name: '张三', title: 'Python编程：从入门到实践', author: 'Eric Matthes', isbn: '978-7-111-53551-1', condition: 'good', price: 45.0, description: '已阅读完毕，状态良好', status: 'available', contact: '13800000002' },
                    { id: 2, user_id: 4, seller_name: '李四', title: 'JavaScript高级程序设计', author: 'Nicholas C. Zakas', isbn: '978-7-115-42857-7', condition: 'like_new', price: 80.0, description: '全新未拆封', status: 'available', contact: '13800000003' },
                    { id: 3, user_id: 5, seller_name: '王五', title: '数据结构与算法分析', author: 'Mark Allen Weiss', isbn: '978-7-302-41580-7', condition: 'fair', price: 30.0, description: '有少量笔记', status: 'available', contact: '13800000004' },
                    { id: 4, user_id: 6, seller_name: '赵六', title: '算法导论', author: 'Thomas H. Cormen', isbn: '978-7-111-40701-0', condition: 'good', price: 60.0, description: '经典算法教材，有划线笔记', status: 'available', contact: '13800000005' },
                    { id: 5, user_id: 7, seller_name: '钱七', title: '深度学习', author: 'Ian Goodfellow', isbn: '978-7-111-58165-5', condition: 'like_new', price: 120.0, description: '全新正版，刚买不久', status: 'available', contact: '13800000006' },
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
            this.loadOverdueRecords();
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
        loadOverdueRecords() {
            this.overdueRecords = this.borrowRecords.filter(r => r.status === 'overdue');
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
            this.currentBookPage = 1;
        },
        goToBookPage(page) {
            if (page >= 1 && page <= this.totalBookPages) {
                this.currentBookPage = page;
            }
        },
        viewBook(book) {
            alert(`书名: ${book.title}\n作者: ${book.author}\n出版社: ${book.publisher}\n分类: ${book.category}\n位置: ${book.location}\n价格: ${book.price}元\n库存: ${book.available_stock}/${book.total_stock}\n简介: ${book.description}`);
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
        searchSecondhand() {},
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
            this.secondhandForm = { title: '', author: '', isbn: '', condition: 'good', price: 0, description: '', contact: '' };
            this.saveData();
            alert('发布成功');
        },
        viewSecondhandDetail(book) {
            this.selectedSecondhandBook = book;
            $('#showSecondhandDetail').modal('show');
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
            alert('交易申请已提交，请联系卖家：' + book.contact);
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
                    this.currentBookPage = 1;
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