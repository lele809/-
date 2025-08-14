from flask import Flask
from flask import Flask, render_template, redirect, jsonify, request, Response, url_for, flash, session, send_file
from models import db, ContactsOld, ContactsNew, RentalOld, RentalNew, RentalRecordsOld, RentalRecordsNew, RoomsNew, \
    RoomsOld, RentalInfoOld, RentalInfoNew, ContractsOld, ContractsNew, Admin
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import zipfile
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from sqlalchemy import extract, and_

app = Flask(__name__)

try:
    app.config.from_object('config.Config')
    db.init_app(app)
    print("✅ 数据库初始化成功")
except Exception as e:
    print(f"❌ 数据库初始化失败: {str(e)}")
    print("🔧 尝试使用SQLite备用数据库...")
    # 强制使用SQLite作为备用
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), 'rent_system_emergency.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print(f"✅ 使用紧急SQLite数据库: {db_path}")


# 全局上下文处理器 - 使所有模板都能访问当前管理员信息
@app.context_processor
def inject_admin_info():
    """向所有模板注入管理员信息"""
    admin_info = {
        'current_admin_name': session.get('admin_name', '未登录'),
        'current_admin_id': session.get('admin_id'),
        'is_logged_in': 'admin_id' in session
    }
    return admin_info


def get_todo_items(floor='old'):
    """获取待办事项数据
    Args:
        floor (str): 'old' 表示五楼，'new' 表示六楼
    """
    from datetime import datetime, timedelta

    todo_items = {
        'contract_expiring': [],
        'unpaid_rent': [],
        'maintenance_completed': []
    }

    # 根据楼层选择对应的数据表
    if floor == 'old':
        ContractsModel = ContractsOld
        RentalModel = RentalOld
        RoomsModel = RoomsOld
    else:  # floor == 'new'
        ContractsModel = ContractsNew
        RentalModel = RentalNew
        RoomsModel = RoomsNew

    # 1. 合同到期提醒（30天内到期的合同）
    today = datetime.now().date()
    expiry_threshold = today + timedelta(days=30)

    expiring_contracts = ContractsModel.query.filter(
        and_(
            ContractsModel.contract_end_date <= expiry_threshold,
            ContractsModel.contract_end_date >= today,
            ContractsModel.contract_status == 1  # 有效合同
        )
    ).all()

    for contract in expiring_contracts:
        days_left = (contract.contract_end_date - today).days
        todo_items['contract_expiring'].append({
            'room_number': contract.room_number,
            'tenant_name': contract.tenant_name,
            'end_date': contract.contract_end_date,
            'days_left': days_left
        })

    # 2. 缴费提醒（未缴费的租金）
    unpaid_rentals = RentalModel.query.filter_by(payment_status=2).all()
    for rental in unpaid_rentals:
        todo_items['unpaid_rent'].append({
            'room_number': rental.room_number,
            'tenant_name': rental.tenant_name,
            'total_due': float(rental.total_due) if rental.total_due else 0.0
        })

    # 3. 维修完成提醒（最近7天内状态从维修中变为其他状态的房间）
    # 这里简化处理，获取当前非维修状态但之前可能是维修状态的房间
    recent_maintenance = RoomsModel.query.filter(
        RoomsModel.room_status.in_([1, 2])  # 空闲或已出租
    ).limit(3).all()  # 限制显示数量

    for room in recent_maintenance:
        if room.updated_at and room.updated_at.date() >= (today - timedelta(days=7)):
            todo_items['maintenance_completed'].append({
                'room_number': room.room_number,
                'status': '维修完成' if room.room_status == 1 else '维修完成并已出租'
            })

    return todo_items


@app.route('/test')
def test_route():
    """测试路由 - 确保代码更新生效"""
    return "<h1>🎉 代码更新成功！</h1><p>路由正常工作</p><a href='/init_db'>点击初始化数据库</a>"


@app.route('/init_db')
def init_db_simple():
    """简单的数据库初始化路由"""
    try:
        from models import Admin
        from werkzeug.security import generate_password_hash
        
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员
        existing = Admin.query.first()
        if existing:
            return f"<h1>✅ 数据库已初始化</h1><p>管理员: {existing.admin_name}</p><a href='/login'>前往登录</a>"
        
        # 创建管理员
        admin = Admin(
            admin_name='admin',
            password=generate_password_hash('123456')
        )
        db.session.add(admin)
        db.session.commit()
        
        return """
        <h1>🎉 数据库初始化成功！</h1>
        <p>✅ 表创建完成</p>
        <p>✅ 管理员账户创建完成</p>
        <h2>登录信息：</h2>
        <p>用户名: admin</p>
        <p>密码: 123456</p>
        <a href='/login'>前往登录</a>
        """
        
    except Exception as e:
        return f"<h1>❌ 初始化失败</h1><p>错误: {str(e)}</p>"


@app.route('/health')
def health_check():
    """健康检查路由 - 用于调试部署问题"""
    try:
        # 检查数据库连接
        db.session.execute(db.text('SELECT 1'))
        db_status = "✅ 数据库连接正常"
        
        # 检查表是否存在
        try:
            admin_count = Admin.query.count()
            table_status = f"✅ Admin表存在，共有 {admin_count} 个管理员账户"
        except Exception:
            table_status = "❌ Admin表不存在，需要初始化数据库"
            
    except Exception as e:
        db_status = f"❌ 数据库连接失败: {str(e)}"
        table_status = "❌ 无法检查表状态"
    
    # 检查配置
    config_info = {
        'SECRET_KEY': '已设置' if app.config.get('SECRET_KEY') else '未设置',
        'DATABASE_URI': app.config.get('SQLALCHEMY_DATABASE_URI', '未设置')[:50] + '...' if app.config.get('SQLALCHEMY_DATABASE_URI') else '未设置'
    }
    
    return f"""
    <html>
    <head>
        <title>租房系统健康检查</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .success {{ color: green; }}
            .error {{ color: red; }}
            .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>租房系统健康检查</h1>
        
        <h2>数据库状态</h2>
        <p class="{'success' if '✅' in db_status else 'error'}">{db_status}</p>
        
        <h2>数据库表状态</h2>
        <p class="{'success' if '✅' in table_status else 'error'}">{table_status}</p>
        
        <h2>配置信息</h2>
        <ul>
            <li>SECRET_KEY: {config_info['SECRET_KEY']}</li>
            <li>DATABASE_URI: {config_info['DATABASE_URI']}</li>
        </ul>
        
        <h2>操作</h2>
        <a href="/setup_database" class="button">🔧 初始化数据库</a>
        <a href="/login" class="button">🏠 返回登录页</a>
    </body>
    </html>
    """


@app.route('/setup_database')
def setup_database():
    """数据库初始化路由 - 通过网页访问初始化数据库"""
    try:
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员账户
        existing_admin = Admin.query.first()
        if existing_admin:
            return f"""
            <html>
            <head>
                <title>数据库初始化</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .success {{ color: green; }}
                    .info {{ color: blue; }}
                    .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <h1>数据库初始化结果</h1>
                <p class="success">✅ 数据库表已存在</p>
                <p class="info">ℹ️ 管理员账户已存在: {existing_admin.admin_name}</p>
                <p class="info">数据库无需重复初始化</p>
                
                <h2>操作</h2>
                <a href="/login" class="button">🏠 前往登录</a>
                <a href="/health" class="button">🔧 健康检查</a>
            </body>
            </html>
            """
        
        # 创建默认管理员账户
        from werkzeug.security import generate_password_hash
        admin = Admin(
            admin_name='admin',
            password=generate_password_hash('123456')
        )
        db.session.add(admin)
        db.session.commit()
        
        return f"""
        <html>
        <head>
            <title>数据库初始化成功</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .success {{ color: green; }}
                .important {{ background-color: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px; }}
                .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>🎉 数据库初始化成功！</h1>
            
            <p class="success">✅ 数据库表创建完成</p>
            <p class="success">✅ 默认管理员账户创建完成</p>
            
            <div class="important">
                <h3>🔑 登录信息</h3>
                <p><strong>用户名:</strong> admin</p>
                <p><strong>密码:</strong> 123456</p>
                <p><strong>⚠️ 重要:</strong> 请在首次登录后立即修改密码！</p>
            </div>
            
            <h2>操作</h2>
            <a href="/login" class="button">🏠 前往登录</a>
            <a href="/health" class="button">🔧 健康检查</a>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>数据库初始化失败</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: red; }}
                .button {{ background-color: #f44336; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>❌ 数据库初始化失败</h1>
            
            <p class="error">错误详情: {str(e)}</p>
            
            <h2>可能的解决方案</h2>
            <ul>
                <li>检查数据库连接是否正常</li>
                <li>确认环境变量配置正确</li>
                <li>稍后重试初始化</li>
            </ul>
            
            <h2>操作</h2>
            <a href="/setup_database" class="button">🔄 重试初始化</a>
            <a href="/health" class="button">🔧 健康检查</a>
        </body>
        </html>
        """


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面和处理"""
    if request.method == 'POST':
        admin_name = request.form.get('admin_name')
        password = request.form.get('password')

        if not admin_name or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')

        # 查找管理员账户
        admin = Admin.query.filter_by(admin_name=admin_name).first()

        if admin and admin.check_password(password):
            # 登录成功
            session['admin_id'] = admin.id
            session['admin_name'] = admin.admin_name

            # 更新最后登录时间
            admin.last_login = datetime.now()
            db.session.commit()

            flash('登录成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))


@app.route('/')
def home():
    """首页重定向到登录页面"""
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    # 检查登录状态
    if 'admin_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/base_old')
def base_old():
    return render_template('base_old.html')


@app.route('/base_new')
def base_new():
    return render_template('base_new.html')


@app.route('/index5')
def index5():
    from datetime import datetime, timedelta
    from sqlalchemy import extract, and_

    # 基本统计数据
    total_contacts = ContactsOld.query.count()
    total_rental = RentalOld.query.count()
    total_records = RentalRecordsOld.query.count()

    # 房间统计数据
    total_rooms = RoomsOld.query.count()
    rented_rooms = RoomsOld.query.filter_by(room_status=2).count()  # 已出租
    vacant_rooms = RoomsOld.query.filter_by(room_status=1).count()  # 空闲

    # 未交房租统计
    unpaid_rentals = RentalOld.query.filter_by(payment_status=2).all()  # 未缴费
    unpaid_rooms_count = len(unpaid_rentals)

    # 获取未交房租的详细信息
    unpaid_room_details = []
    for rental in unpaid_rentals:
        unpaid_room_details.append({
            'room_number': rental.room_number,
            'tenant_name': rental.tenant_name,
            'total_due': float(rental.total_due) if rental.total_due else 0.0
        })

    # 计算本月收入（基于缴费记录表的实际缴费日期）
    current_month = datetime.now().month
    current_year = datetime.now().year

    # 从缴费记录表获取本月收入
    monthly_records = RentalRecordsOld.query.filter(
        extract('month', RentalRecordsOld.payment_date) == current_month,
        extract('year', RentalRecordsOld.payment_date) == current_year
    ).all()

    monthly_income = sum([float(record.total_rent) for record in monthly_records if record.total_rent])

    # 水电费收入（从租赁表中获取本月已缴费的水电费）
    utilities_income = sum(
        [float(rental.utilities_fee) for rental in RentalOld.query.filter_by(payment_status=1).all() if
         rental.utilities_fee])

    # 获取待办事项数据
    todo_items = get_todo_items('old')

    stats = {
        'total_contacts': total_contacts,
        'total_rental': total_rental,
        'total_records': total_records,
        'total_rooms': total_rooms,
        'rented_rooms': rented_rooms,
        'vacant_rooms': vacant_rooms,
        'unpaid_rooms': unpaid_rooms_count,
        'unpaid_room_details': unpaid_room_details,
        'monthly_income': monthly_income,
        'utilities_income': utilities_income,
        'todo_items': todo_items
    }

    return render_template('index5.html', stats=stats)


@app.route('/index6')
def index6():
    from datetime import datetime, timedelta
    from sqlalchemy import extract, and_

    # 基本统计数据
    total_contacts = ContactsNew.query.count()
    total_rental = RentalNew.query.count()
    total_records = RentalRecordsNew.query.count()

    # 房间统计数据
    total_rooms = RoomsNew.query.count()
    rented_rooms = RoomsNew.query.filter_by(room_status=2).count()  # 已出租
    vacant_rooms = RoomsNew.query.filter_by(room_status=1).count()  # 空闲

    # 未交房租统计
    unpaid_rentals = RentalNew.query.filter_by(payment_status=2).all()  # 未缴费
    unpaid_rooms_count = len(unpaid_rentals)

    # 获取未交房租的详细信息
    unpaid_room_details = []
    for rental in unpaid_rentals:
        unpaid_room_details.append({
            'room_number': rental.room_number,
            'tenant_name': rental.tenant_name,
            'total_due': float(rental.total_due) if rental.total_due else 0.0
        })

    # 计算本月收入（基于缴费记录表的实际缴费日期）
    current_month = datetime.now().month
    current_year = datetime.now().year

    # 从缴费记录表获取本月收入
    monthly_records = RentalRecordsNew.query.filter(
        extract('month', RentalRecordsNew.payment_date) == current_month,
        extract('year', RentalRecordsNew.payment_date) == current_year
    ).all()

    monthly_income = sum([float(record.total_rent) for record in monthly_records if record.total_rent])

    # 水电费收入（从租赁表中获取本月已缴费的水电费）
    utilities_income = sum(
        [float(rental.utilities_fee) for rental in RentalNew.query.filter_by(payment_status=1).all() if
         rental.utilities_fee])

    # 获取待办事项数据
    todo_items = get_todo_items('new')

    stats = {
        'total_contacts': total_contacts,
        'total_rental': total_rental,
        'total_records': total_records,
        'total_rooms': total_rooms,
        'rented_rooms': rented_rooms,
        'vacant_rooms': vacant_rooms,
        'unpaid_rooms': unpaid_rooms_count,
        'unpaid_room_details': unpaid_room_details,
        'monthly_income': monthly_income,
        'utilities_income': utilities_income,
        'todo_items': todo_items
    }

    return render_template('index6.html', stats=stats)


@app.route('/contacts_old')
def contacts_old():
    page = request.args.get('page', 1, type=int)
    view_type = request.args.get('view_type', 'card')  # 默认卡片视图

    # 根据视图类型设置每页显示数量
    if view_type == 'table':
        per_page = 10  # 表格视图每页10条数据
        min_for_pagination = 10
    else:
        per_page = 12  # 卡片视图每页12条数据
        min_for_pagination = 12

    # 先查询总数
    total_count = ContactsOld.query.count()
    
    # 计算本周新增联系人数量
    from datetime import datetime, timedelta
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    weekly_new_count = ContactsOld.query.filter(
        ContactsOld.created_at >= week_start
    ).count()

    if total_count <= min_for_pagination:
        # 如果总数不超过最小分页数量，直接返回所有数据，不分页
        contacts_list = ContactsOld.query.all()
        return render_template('contacts_old.html',
                               contacts_list=contacts_list,
                               pagination=None,
                               current_view_type=view_type,
                               weekly_new_count=weekly_new_count)
    else:
        # 超过最小分页数量才进行分页
        contacts_pagination = ContactsOld.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        contacts_list = contacts_pagination.items
        return render_template('contacts_old.html',
                               contacts_list=contacts_list,
                               pagination=contacts_pagination,
                               current_view_type=view_type,
                               weekly_new_count=weekly_new_count)


@app.route('/rooms_old')
def rooms_old():
    rooms_list = RoomsOld.query.all()

    # 计算房间统计信息
    total_rooms = len(rooms_list)
    available_rooms = len([r for r in rooms_list if r.room_status == 1])
    occupied_rooms = len([r for r in rooms_list if r.room_status == 2])
    maintenance_rooms = len([r for r in rooms_list if r.room_status == 3])
    disabled_rooms = len([r for r in rooms_list if r.room_status == 4])

    room_stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'disabled_rooms': disabled_rooms
    }

    return render_template('rooms_old.html', rooms_list=rooms_list, room_stats=room_stats)


@app.route('/rooms_new')
def rooms_new():
    rooms_list = RoomsNew.query.all()

    # 计算房间统计信息
    total_rooms = len(rooms_list)
    available_rooms = len([r for r in rooms_list if r.room_status == 1])
    occupied_rooms = len([r for r in rooms_list if r.room_status == 2])
    maintenance_rooms = len([r for r in rooms_list if r.room_status == 3])
    disabled_rooms = len([r for r in rooms_list if r.room_status == 4])

    room_stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'disabled_rooms': disabled_rooms
    }

    return render_template('rooms_new.html', rooms_list=rooms_list, room_stats=room_stats)


@app.route('/contacts_new')
def contacts_new():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页10条数据
    
    # 计算本周新增联系人数量
    from datetime import datetime, timedelta
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    weekly_new_count = ContactsNew.query.filter(
        ContactsNew.created_at >= week_start
    ).count()

    # 总是进行分页处理，确保模板能正确显示分页信息
    contacts_pagination = ContactsNew.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    contacts_list = contacts_pagination.items
    return render_template('contacts_new.html',
                           contacts_list=contacts_list,
                           pagination=contacts_pagination,
                           weekly_new_count=weekly_new_count)


@app.route('/rental_old')
def rental_old():
    # 获取日期筛选参数
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    # 构建查询
    query = RentalOld.query

    # 如果有年月筛选参数，则按created_at进行筛选
    if year and month:
        from calendar import monthrange

        # 获取该月的第一天和最后一天
        start_date = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59)

        query = query.filter(RentalOld.created_at >= start_date, RentalOld.created_at <= end_date)

    rental_list = query.order_by(RentalOld.created_at.desc()).all()

    # 获取所有记录的最早创建时间，用于日历筛选的起始时间
    earliest_record = db.session.query(RentalOld.created_at).order_by(RentalOld.created_at.asc()).first()
    earliest_date = earliest_record[0] if earliest_record else datetime.now()

    return render_template('rental_old.html',
                           rental_list=rental_list,
                           current_year=year,
                           current_month=month,
                           earliest_date=earliest_date)


@app.route('/rental_new')
def rental_new():
    rental_list = RentalNew.query.all()
    return render_template('rental_new.html', rental_list=rental_list)


@app.route('/rental_info_old')
def rental_info_old():
    rental_info_list = RentalInfoOld.query.all()
    return render_template('rental_info_old.html', rental_info_list=rental_info_list)


@app.route('/rental_info_new')
def rental_info_new():
    rental_info_list = RentalInfoNew.query.all()
    return render_template('rental_info_new.html', rental_info_list=rental_info_list)


@app.route('/contracts_old')
def contracts_old():
    # 获取合同列表
    contracts_list = ContractsOld.query.all()

    # 获取房间列表用于筛选
    rooms_list = RoomsOld.query.all()

    # 计算统计数据
    total_contracts = len(contracts_list)
    active_contracts = 0
    expiring_contracts = 0
    expired_contracts = 0

    # 如果有合同数据，计算各种状态的合同数量
    if contracts_list:
        current_date = datetime.now().date()
        for contract in contracts_list:
            if contract.contract_status == 1:  # 有效合同
                if contract.contract_end_date:
                    days_to_expire = (contract.contract_end_date - current_date).days
                    if days_to_expire > 30:
                        active_contracts += 1
                    elif days_to_expire > 0:
                        expiring_contracts += 1
                    else:
                        expired_contracts += 1
                else:
                    active_contracts += 1
            else:
                expired_contracts += 1  # 失效合同

    contract_stats = {
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'expiring_contracts': expiring_contracts,
        'expired_contracts': expired_contracts
    }

    return render_template('contracts_old.html',
                           contracts_list=contracts_list,
                           rooms_list=rooms_list,
                           contract_stats=contract_stats,
                           current_date=datetime.now().date())


@app.route('/contracts_new')
def contracts_new():
    # 获取合同列表
    contracts_list = ContractsNew.query.all()

    # 获取房间列表用于筛选
    rooms_list = RoomsNew.query.all()

    # 计算统计数据
    total_contracts = len(contracts_list)
    active_contracts = 0
    expiring_contracts = 0
    expired_contracts = 0

    # 如果有合同数据，计算各种状态的合同数量
    if contracts_list:
        current_date = datetime.now().date()
        for contract in contracts_list:
            if contract.contract_status == 1:  # 有效合同
                if contract.contract_end_date:
                    days_to_expire = (contract.contract_end_date - current_date).days
                    if days_to_expire > 30:
                        active_contracts += 1
                    elif days_to_expire > 0:
                        expiring_contracts += 1
                    else:
                        expired_contracts += 1
                else:
                    active_contracts += 1
            else:
                expired_contracts += 1  # 失效合同

    contract_stats = {
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'expiring_contracts': expiring_contracts,
        'expired_contracts': expired_contracts
    }

    return render_template('contracts_new.html',
                           contracts_list=contracts_list,
                           rooms_list=rooms_list,
                           contract_stats=contract_stats,
                           current_date=datetime.now().date())


@app.route('/rental_records_old')
def rental_records_old():
    rental_records_list = RentalRecordsOld.query.all()
    return render_template('rental_records_old.html', rental_records_list=rental_records_list)


@app.route('/rental_records_new')
def rental_records_new():
    rental_records_list = RentalRecordsNew.query.all()
    return render_template('rental_records_new.html', rental_records_list=rental_records_list)


# 联系人管理路由
@app.route('/contacts_old/add', methods=['GET', 'POST'])
def contacts_add():
    """添加联系人页面和处理"""
    if request.method == 'POST':
        try:
            data = request.get_json()

            # 检查电话号码是否已存在
            existing_contact = ContactsOld.query.filter_by(phone=data['phone']).first()
            if existing_contact:
                return jsonify({'success': False, 'message': '电话号码已存在'})

            # 创建新联系人
            new_contact = ContactsOld(
                name=data['name'],
                roomId=data['roomId'],
                phone=data['phone'],
                id_card=data['id_card']
            )

            db.session.add(new_contact)
            db.session.commit()

            return jsonify({'success': True, 'message': '联系人添加成功'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

    return render_template('contacts_old.html')


# API路由 - 房间管理
@app.route('/api/rooms_old', methods=['POST'])
def api_add_room_old():
    """添加五楼房间"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_room = RoomsOld.query.filter_by(room_number=data['room_number']).first()
        if existing_room:
            return jsonify({'success': False, 'message': '房号已存在'})

        new_room = RoomsOld(
            room_number=data['room_number'],
            room_type=data['room_type'],
            base_rent=float(data['base_rent']),
            deposit=float(data.get('deposit', 0.00)),
            room_status=int(data['room_status']),
            water_meter_number=data['water_meter_number'],
            electricity_meter_number=data['electricity_meter_number']
        )

        db.session.add(new_room)
        db.session.commit()

        return jsonify({'success': True, 'message': '房间添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 房间详情
@app.route('/api/rooms_old/<int:room_id>', methods=['GET'])
def api_get_room_old(room_id):
    """获取五楼房间详情"""
    try:
        room = RoomsOld.query.get_or_404(room_id)

        status_map = {
            1: '空闲',
            2: '已出租',
            3: '维修中',
            4: '停用'
        }

        room_data = {
            'id': room.id,
            'room_number': room.room_number,
            'room_type': room.room_type,
            'base_rent': float(room.base_rent),
            'deposit': float(room.deposit),
            'status': room.room_status,
            'status_text': status_map.get(room.room_status, '未知'),
            'water_meter_number': room.water_meter_number,
            'electricity_meter_number': room.electricity_meter_number,
            'created_at': room.created_at.strftime('%Y-%m-%d %H:%M:%S') if room.created_at else '-',
            'updated_at': room.updated_at.strftime('%Y-%m-%d %H:%M:%S') if room.updated_at else '-'
        }

        return jsonify(room_data)
    except Exception as e:
        return jsonify({'error': f'获取房间信息失败: {str(e)}'})


# 联系人详情API
@app.route('/api/contacts_old/<int:contact_id>', methods=['GET'])
def api_get_contact(contact_id):
    """获取联系人详情"""
    try:
        contact = ContactsOld.query.get_or_404(contact_id)

        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'roomId': contact.roomId,
            'phone': contact.phone,
            'id_card': contact.id_card,
            'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M:%S') if contact.created_at else '-'
        }
        return jsonify(contact_data)
    except Exception as e:
        return jsonify({'error': f'获取联系人信息失败: {str(e)}'})


# 删除房间
@app.route('/api/rooms_old/<int:room_id>', methods=['DELETE'])
def api_delete_room_old(room_id):
    """删除五楼房间"""
    try:
        room = RoomsOld.query.get_or_404(room_id)

        # 检查房间是否有关联的租赁记录
        rental_count = RentalOld.query.filter_by(room_number=room.room_number).count()
        if rental_count > 0:
            return jsonify({'success': False, 'message': '该房间有租赁记录，无法删除'})

        db.session.delete(room)
        db.session.commit()

        return jsonify({'success': True, 'message': '房间删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 六楼房间管理API
@app.route('/api/rooms_new', methods=['POST'])
def api_add_room_new():
    """添加六楼房间"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_room = RoomsNew.query.filter_by(room_number=data['room_number']).first()
        if existing_room:
            return jsonify({'success': False, 'message': '房号已存在'})

        new_room = RoomsNew(
            room_number=data['room_number'],
            room_type=data['room_type'],
            base_rent=float(data['base_rent']),
            deposit=float(data.get('deposit', 0.00)),
            room_status=int(data['room_status']),
            water_meter_number=data['water_meter_number'],
            electricity_meter_number=data['electricity_meter_number']
        )

        db.session.add(new_room)
        db.session.commit()

        return jsonify({'success': True, 'message': '房间添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 获取六楼房间详情
@app.route('/api/rooms_new/<int:room_id>', methods=['GET'])
def api_get_room_new(room_id):
    """获取六楼房间详情"""
    try:
        room = RoomsNew.query.get_or_404(room_id)

        status_map = {
            1: '空闲',
            2: '已出租',
            3: '维修中',
            4: '停用'
        }

        room_data = {
            'id': room.id,
            'room_number': room.room_number,
            'room_type': room.room_type,
            'base_rent': float(room.base_rent),
            'deposit': float(room.deposit),
            'status': room.room_status,
            'status_text': status_map.get(room.room_status, '未知'),
            'water_meter_number': room.water_meter_number,
            'electricity_meter_number': room.electricity_meter_number,
            'created_at': room.created_at.strftime('%Y-%m-%d %H:%M:%S') if room.created_at else '-',
            'updated_at': room.updated_at.strftime('%Y-%m-%d %H:%M:%S') if room.updated_at else '-'
        }

        return jsonify(room_data)
    except Exception as e:
        return jsonify({'error': f'获取房间信息失败: {str(e)}'})


# 更新六楼房间信息
@app.route('/api/rooms_new/<int:room_id>', methods=['PUT'])
def api_update_room_new(room_id):
    """更新六楼房间信息"""
    try:
        room = RoomsNew.query.get_or_404(room_id)
        data = request.get_json()

        # 检查房号是否已被其他房间使用
        if data['room_number'] != room.room_number:
            existing_room = RoomsNew.query.filter_by(room_number=data['room_number']).first()
            if existing_room:
                return jsonify({'success': False, 'message': '房号已存在'})

        # 更新房间信息
        room.room_number = data['room_number']
        room.room_type = data['room_type']
        room.base_rent = float(data['base_rent'])
        room.deposit = float(data.get('deposit', 0.00))
        room.room_status = int(data['room_status'])
        room.water_meter_number = data['water_meter_number']
        room.electricity_meter_number = data['electricity_meter_number']

        db.session.commit()

        return jsonify({'success': True, 'message': '房间更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 删除六楼房间
@app.route('/api/rooms_new/<int:room_id>', methods=['DELETE'])
def api_delete_room_new(room_id):
    """删除六楼房间"""
    try:
        room = RoomsNew.query.get_or_404(room_id)

        # 检查房间是否有关联的租赁记录
        rental_count = RentalNew.query.filter_by(room_number=room.room_number).count()
        if rental_count > 0:
            return jsonify({'success': False, 'message': '该房间有租赁记录，无法删除'})

        db.session.delete(room)
        db.session.commit()

        return jsonify({'success': True, 'message': '房间删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 获取六楼联系人详情
@app.route('/api/contacts_new/<int:contact_id>', methods=['GET'])
def api_get_contact_new(contact_id):
    """获取六楼联系人详情"""
    try:
        contact = ContactsNew.query.get_or_404(contact_id)

        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'roomId': contact.roomId,
            'phone': contact.phone,
            'id_card': contact.id_card,
            'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M:%S') if contact.created_at else '-'
        }
        return jsonify(contact_data)
    except Exception as e:
        return jsonify({'error': f'获取联系人信息失败: {str(e)}'})


# 删除六楼联系人
@app.route('/api/contacts_new/<int:contact_id>', methods=['DELETE'])
def api_delete_contact_new(contact_id):
    """删除六楼联系人"""
    try:
        contact = ContactsNew.query.get_or_404(contact_id)

        # 检查联系人是否有关联的租赁记录

        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '联系人删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 更新六楼联系人信息
@app.route('/api/contacts_new/<int:contact_id>', methods=['PUT'])
def api_update_contact_new(contact_id):
    """更新六楼联系人信息"""
    try:
        contact = ContactsNew.query.get_or_404(contact_id)
        data = request.get_json()

        # 更新联系人信息
        contact.name = data['name']
        contact.roomId = data['roomId']
        contact.phone = data['phone']
        contact.id_card = data['id_card']

        db.session.commit()

        return jsonify({'success': True, 'message': '联系人更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 添加六楼联系人
@app.route('/contacts_new/add', methods=['GET', 'POST'])
def contacts_new_add():
    """添加六楼联系人页面和处理"""
    if request.method == 'POST':
        try:
            data = request.get_json()

            # 检查电话号码是否已存在
            existing_contact = ContactsNew.query.filter_by(phone=data['phone']).first()
            if existing_contact:
                return jsonify({'success': False, 'message': '电话号码已存在'})

            # 创建新联系人
            new_contact = ContactsNew(
                name=data['name'],
                roomId=data['roomId'],
                phone=data['phone'],
                id_card=data['id_card']
            )

            db.session.add(new_contact)
            db.session.commit()

            return jsonify({'success': True, 'message': '联系人添加成功'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

    return render_template('contacts_new.html')


# 删除五楼联系人
@app.route('/api/contacts_old/<int:contact_id>', methods=['DELETE'])
def api_delete_contact_old(contact_id):
    """删除联系人"""
    try:
        contact = ContactsOld.query.get_or_404(contact_id)

        # 检查联系人是否有关联的租赁记录

        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '联系人删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 更新房间信息
@app.route('/api/rooms_old/<int:room_id>', methods=['PUT'])
def api_update_room_old(room_id):
    """更新五楼房间信息"""
    try:
        room = RoomsOld.query.get_or_404(room_id)
        data = request.get_json()

        # 检查房号是否已被其他房间使用
        if data['room_number'] != room.room_number:
            existing_room = RoomsOld.query.filter_by(room_number=data['room_number']).first()
            if existing_room:
                return jsonify({'success': False, 'message': '房号已存在'})

        # 更新房间信息
        room.room_number = data['room_number']
        room.room_type = data['room_type']
        room.base_rent = float(data['base_rent'])
        room.deposit = float(data.get('deposit', 0.00))
        room.room_status = int(data['room_status'])
        room.water_meter_number = data['water_meter_number']
        room.electricity_meter_number = data['electricity_meter_number']

        db.session.commit()

        return jsonify({'success': True, 'message': '房间更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 更新联系人信息
@app.route('/api/contacts_old/<int:contact_id>', methods=['PUT'])
def api_update_contact_old(contact_id):
    """更新联系人信息"""
    try:
        contact = ContactsOld.query.get_or_404(contact_id)
        data = request.get_json()

        # 检查联系人是否已被其他联系人使用
        if data['phone'] != contact.phone:
            existing_contact = ContactsOld.query.filter_by(phone=data['phone']).first()
            if existing_contact:
                return jsonify({'success': False, 'message': '电话号码已存在'})

        # 更新联系人信息
        contact.name = data['name']
        contact.roomId = data['roomId']
        contact.phone = data['phone']
        contact.id_card = data['id_card']

        db.session.commit()

        return jsonify({'success': True, 'message': '联系人更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 五楼联系人API
@app.route('/api/contacts_old', methods=['POST'])
def api_contacts_old():
    """添加五楼联系人"""
    try:
        data = request.get_json()

        # 检查联系人是否存在
        exist_contact = ContactsOld.query.filter_by(phone=data['phone']).first()
        if exist_contact:
            return jsonify({'success': False, 'message': '电话号码已存在'})
        new_contact = ContactsOld(
            phone=data['phone'],
            name=data['name'],
            roomId=data['roomId'],
            id_card=data['id_card']
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '联系人添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 联系人
@app.route('/api/contacts', methods=['POST'])
def api_contacts():
    """添加联系人"""
    try:
        data = request.get_json()

        # 检查联系人是否存在
        exist_contact = ContactsOld.query.filter_by(phone=data['phone']).first()
        if exist_contact:
            return jsonify({'success': False, 'message': '电话号码已存在'})
        new_contact = ContactsOld(
            phone=data['phone'],
            name=data['name'],
            roomId=data['roomId'],
            id_card=data['id_card']
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '联系人添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 六楼联系人API
@app.route('/api/contacts_new', methods=['POST'])
def api_contacts_new():
    """添加六楼联系人"""
    try:
        data = request.get_json()

        # 检查联系人是否存在
        exist_contact = ContactsNew.query.filter_by(phone=data['phone']).first()
        if exist_contact:
            return jsonify({'success': False, 'message': '电话号码已存在'})
        new_contact = ContactsNew(
            phone=data['phone'],
            name=data['name'],
            roomId=data['roomId'],
            id_card=data['id_card']
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '联系人添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 租房信息详情API
@app.route('/api/rental_info_old/<int:info_id>', methods=['GET'])
def api_get_rental_info_old(info_id):
    """获取租房信息详情"""
    try:
        info = RentalInfoOld.query.get_or_404(info_id)

        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        info_data = {
            'id': info.id,
            'room_number': info.room_number,
            'tenant_name': info.tenant_name,
            'phone': info.phone,
            'deposit': float(info.deposit) if info.deposit else 0,
            'occupant_count': info.occupant_count,
            'check_in_date': info.check_in_date.strftime('%Y-%m-%d') if info.check_in_date else '',
            'rental_status': info.rental_status,
            'rental_status_text': status_map.get(info.rental_status, '未知'),
            'remarks': info.remarks or '',
            'created_at': info.created_at.strftime('%Y-%m-%d %H:%M:%S') if info.created_at else '-',
            'updated_at': info.updated_at.strftime('%Y-%m-%d %H:%M:%S') if info.updated_at else '-'
        }

        return jsonify(info_data)
    except Exception as e:
        return jsonify({'error': f'获取租房信息失败: {str(e)}'})


# 搜索租房信息API
@app.route('/api/rental_info_old/search', methods=['GET'])
def api_search_rental_info_old():
    """搜索租房信息"""
    try:
        search_term = request.args.get('q', '').strip()
        filter_status = request.args.get('status', 'all')

        # 构建查询
        query = RentalInfoOld.query

        # 添加搜索条件
        if search_term:
            search_filter = db.or_(
                RentalInfoOld.room_number.like(f'%{search_term}%'),
                RentalInfoOld.tenant_name.like(f'%{search_term}%'),
                RentalInfoOld.phone.like(f'%{search_term}%')
            )
            query = query.filter(search_filter)

        # 添加状态筛选
        if filter_status == 'paid':
            query = query.filter(RentalInfoOld.rental_status == 1)
        elif filter_status == 'unpaid':
            query = query.filter(RentalInfoOld.rental_status == 2)

        # 执行查询
        rental_info_list = query.all()

        # 转换为字典格式
        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        results = []
        for info in rental_info_list:
            results.append({
                'id': info.id,
                'room_number': info.room_number,
                'tenant_name': info.tenant_name,
                'phone': info.phone,
                'deposit': float(info.deposit) if info.deposit else 0,
                'occupant_count': info.occupant_count,
                'check_in_date': info.check_in_date.strftime('%Y-%m-%d') if info.check_in_date else '',
                'rental_status': info.rental_status,
                'rental_status_text': status_map.get(info.rental_status, '未知'),
                'remarks': info.remarks or ''
            })

        return jsonify({
            'success': True,
            'data': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索失败: {str(e)}'})


# 添加租房信息API
@app.route('/api/rental_info_old', methods=['POST'])
def api_add_rental_info_old():
    """添加租房信息"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_info = RentalInfoOld.query.filter_by(room_number=data['room_number']).first()
        if existing_info:
            return jsonify({'success': False, 'message': '该房号已有租房信息'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 创建新记录
        new_info = RentalInfoOld(
            room_number=data['room_number'],
            tenant_name=data['tenant_name'],
            phone=data['phone'],
            deposit=float(data['deposit']) if data.get('deposit') else 0,
            occupant_count=int(data['occupant_count']),
            check_in_date=check_in_date,
            rental_status=int(data['rental_status']),
            remarks=data.get('remarks', '')
        )

        db.session.add(new_info)

        # 更新对应房间状态为已出租
        room = RoomsOld.query.filter_by(room_number=data['room_number']).first()
        if room:
            room.room_status = 2  # 2表示已出租
            room.updated_at = datetime.now()

        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息添加成功，房间状态已更新'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 更新租房信息API
@app.route('/api/rental_info_old/<int:info_id>', methods=['PUT'])
def api_update_rental_info_old(info_id):
    """更新租房信息"""
    try:
        info = RentalInfoOld.query.get_or_404(info_id)
        data = request.get_json()

        # 检查房号是否被其他记录使用
        if data['room_number'] != info.room_number:
            existing_info = RentalInfoOld.query.filter_by(room_number=data['room_number']).first()
            if existing_info:
                return jsonify({'success': False, 'message': '该房号已有其他租房信息'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 更新信息
        info.room_number = data['room_number']
        info.tenant_name = data['tenant_name']
        info.phone = data['phone']
        info.deposit = float(data['deposit']) if data.get('deposit') else 0
        info.occupant_count = int(data['occupant_count'])
        info.check_in_date = check_in_date
        info.rental_status = int(data['rental_status'])
        info.remarks = data.get('remarks', '')

        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息更新成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 删除租房信息API
@app.route('/api/rental_info_old/<int:info_id>', methods=['DELETE'])
def api_delete_rental_info_old(info_id):
    """删除租房信息"""
    try:
        info = RentalInfoOld.query.get_or_404(info_id)

        # 检查是否有关联的租赁记录
        rental_count = RentalOld.query.filter_by(room_number=info.room_number).count()
        if rental_count > 0:
            return jsonify({'success': False, 'message': '该房间有租赁记录，无法删除'})

        db.session.delete(info)
        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 六楼租房信息API
@app.route('/api/rental_info_new/<int:info_id>', methods=['GET'])
def api_get_rental_info_new(info_id):
    """获取六楼租房信息详情"""
    try:
        info = RentalInfoNew.query.get_or_404(info_id)

        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        info_data = {
            'id': info.id,
            'room_number': info.room_number,
            'tenant_name': info.tenant_name,
            'phone': info.phone,
            'deposit': float(info.deposit) if info.deposit else 0,
            'occupant_count': info.occupant_count,
            'check_in_date': info.check_in_date.strftime('%Y-%m-%d') if info.check_in_date else '',
            'rental_status': info.rental_status,
            'rental_status_text': status_map.get(info.rental_status, '未知'),
            'remarks': info.remarks or '',
            'created_at': info.created_at.strftime('%Y-%m-%d %H:%M:%S') if info.created_at else '-',
            'updated_at': info.updated_at.strftime('%Y-%m-%d %H:%M:%S') if info.updated_at else '-'
        }

        return jsonify(info_data)
    except Exception as e:
        return jsonify({'error': f'获取租房信息失败: {str(e)}'})


@app.route('/api/rental_info_new/search', methods=['GET'])
def api_search_rental_info_new():
    """搜索六楼租房信息"""
    try:
        search_term = request.args.get('q', '').strip()
        filter_status = request.args.get('status', 'all')

        # 构建查询
        query = RentalInfoNew.query

        # 添加搜索条件
        if search_term:
            search_filter = db.or_(
                RentalInfoNew.room_number.like(f'%{search_term}%'),
                RentalInfoNew.tenant_name.like(f'%{search_term}%'),
                RentalInfoNew.phone.like(f'%{search_term}%')
            )
            query = query.filter(search_filter)

        # 添加状态筛选
        if filter_status == 'paid':
            query = query.filter(RentalInfoNew.rental_status == 1)
        elif filter_status == 'unpaid':
            query = query.filter(RentalInfoNew.rental_status == 2)

        # 执行查询
        rental_info_list = query.all()

        # 转换为字典格式
        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        results = []
        for info in rental_info_list:
            results.append({
                'id': info.id,
                'room_number': info.room_number,
                'tenant_name': info.tenant_name,
                'phone': info.phone,
                'deposit': float(info.deposit) if info.deposit else 0,
                'occupant_count': info.occupant_count,
                'check_in_date': info.check_in_date.strftime('%Y-%m-%d') if info.check_in_date else '',
                'rental_status': info.rental_status,
                'rental_status_text': status_map.get(info.rental_status, '未知'),
                'remarks': info.remarks or ''
            })

        return jsonify({
            'success': True,
            'data': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索失败: {str(e)}'})


@app.route('/api/rental_info_new', methods=['POST'])
def api_add_rental_info_new():
    """添加六楼租房信息"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_info = RentalInfoNew.query.filter_by(room_number=data['room_number']).first()
        if existing_info:
            return jsonify({'success': False, 'message': '该房号已有租房信息'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 创建新记录
        new_info = RentalInfoNew(
            room_number=data['room_number'],
            tenant_name=data['tenant_name'],
            phone=data['phone'],
            deposit=float(data['deposit']) if data.get('deposit') else 0,
            occupant_count=int(data['occupant_count']),
            check_in_date=check_in_date,
            rental_status=int(data['rental_status']),
            remarks=data.get('remarks', '')
        )

        db.session.add(new_info)

        # 更新对应房间状态为已出租
        room = RoomsNew.query.filter_by(room_number=data['room_number']).first()
        if room:
            room.room_status = 2  # 2表示已出租
            room.updated_at = datetime.now()

        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息添加成功，房间状态已更新'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


@app.route('/api/rental_info_new/<int:info_id>', methods=['PUT'])
def api_update_rental_info_new(info_id):
    """更新六楼租房信息"""
    try:
        info = RentalInfoNew.query.get_or_404(info_id)
        data = request.get_json()

        # 检查房号是否被其他记录使用
        if data['room_number'] != info.room_number:
            existing_info = RentalInfoNew.query.filter_by(room_number=data['room_number']).first()
            if existing_info:
                return jsonify({'success': False, 'message': '该房号已有其他租房信息'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 更新信息
        info.room_number = data['room_number']
        info.tenant_name = data['tenant_name']
        info.phone = data['phone']
        info.deposit = float(data['deposit']) if data.get('deposit') else 0
        info.occupant_count = int(data['occupant_count'])
        info.check_in_date = check_in_date
        info.rental_status = int(data['rental_status'])
        info.remarks = data.get('remarks', '')

        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息更新成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/api/rental_info_new/<int:info_id>', methods=['DELETE'])
def api_delete_rental_info_new(info_id):
    """删除六楼租房信息"""
    try:
        info = RentalInfoNew.query.get_or_404(info_id)

        # 检查是否有关联的租赁记录
        rental_count = RentalNew.query.filter_by(room_number=info.room_number).count()
        if rental_count > 0:
            return jsonify({'success': False, 'message': '该房间有租赁记录，无法删除'})

        db.session.delete(info)
        db.session.commit()

        return jsonify({'success': True, 'message': '租房信息删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 添加租房管理记录API
@app.route('/api/rental_old', methods=['POST'])
def api_add_rental_old():
    """添加租房管理记录"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_rental = RentalOld.query.filter_by(room_number=data['room_number']).first()
        if existing_rental:
            return jsonify({'success': False, 'message': '该房号已有租房记录'})

        # 处理日期字段
        check_in_date = None
        check_out_date = None
        contract_start_date = None
        contract_end_date = None

        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        if data.get('check_out_date'):
            try:
                check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '退房日期格式不正确'})

        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        # 计算应缴费总额
        monthly_rent = float(data.get('monthly_rent', 0))
        water_fee = float(data.get('water_fee', 0))
        electricity_fee = float(data.get('electricity_fee', 0))
        utilities_fee = float(data.get('utilities_fee', 0))

        # 从费用反推用量（前端已经计算好费用，我们需要反推用量）
        water_usage = water_fee / 3.5 if water_fee > 0 else 0  # 水费：3.5元/方
        electricity_usage = electricity_fee / 1.2 if electricity_fee > 0 else 0  # 电费：1.2元/度

        total_due = monthly_rent + utilities_fee

        # 创建新记录
        new_rental = RentalOld(
            room_number=data['room_number'],
            tenant_name=data['tenant_name'],
            deposit=float(data.get('deposit', 0)),
            monthly_rent=monthly_rent,
            water_fee=water_fee,
            electricity_fee=electricity_fee,
            water_usage=water_usage,
            electricity_usage=electricity_usage,
            utilities_fee=utilities_fee,
            total_due=total_due,
            payment_status=int(data.get('payment_status', 2)),  # 默认未缴费
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            remarks=data.get('remarks', '')
        )

        db.session.add(new_rental)
        db.session.commit()

        return jsonify({'success': True, 'message': '租房记录添加成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


# 租房管理详情API
@app.route('/api/rental_old/<int:rental_id>', methods=['GET'])
def api_get_rental_old(rental_id):
    """租房管理详情"""
    try:
        rental = RentalOld.query.get_or_404(rental_id)
        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        rental_data = {
            'id': rental.id,
            'room_number': rental.room_number,
            'tenant_name': rental.tenant_name,
            'deposit': float(rental.deposit) if rental.deposit else 0,
            'monthly_rent': float(rental.monthly_rent) if rental.monthly_rent else 0,
            'water_fee': float(rental.water_fee) if rental.water_fee else 0,
            'electricity_fee': float(rental.electricity_fee) if rental.electricity_fee else 0,
            'water_usage': float(rental.water_usage) if hasattr(rental, 'water_usage') and rental.water_usage else 0,
            'electricity_usage': float(rental.electricity_usage) if hasattr(rental,
                                                                            'electricity_usage') and rental.electricity_usage else 0,
            'utilities_fee': float(rental.utilities_fee) if rental.utilities_fee else 0,
            'total_due': float(rental.total_due) if rental.total_due else 0,
            'payment_status': rental.payment_status,
            'payment_status_text': status_map.get(rental.payment_status, '未知'),
            'remarks': rental.remarks or '',
            'created_at': rental.created_at.strftime('%Y-%m-%d %H:%M:%S') if rental.created_at else '-',
            'updated_at': rental.updated_at.strftime('%Y-%m-%d %H:%M:%S') if rental.updated_at else '-'
        }

        return jsonify(rental_data)
    except Exception as e:
        return jsonify({'error': f'获取租房管理失败: {str(e)}'})


# 编辑租房管理
@app.route('/api/rental_old/<int:rental_id>', methods=['PUT'])
def api_update_rental_old(rental_id):
    """更新租房管理"""
    try:
        rental = RentalOld.query.get_or_404(rental_id)
        data = request.get_json()

        # 检查房号是否被其他记录使用
        if data['room_number'] != rental.room_number:
            existing_info = RentalOld.query.filter_by(room_number=data['room_number']).first()
            if existing_info:
                return jsonify({'success': False, 'message': '该房号已有其他租房管理'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 处理合同开始日期
        contract_start_date = None
        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        # 处理合同结束日期
        contract_end_date = None
        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        # 处理退房日期
        check_out_date = None
        if data.get('check_out_date'):
            try:
                check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '退房日期格式不正确'})

        # 获取费用数据
        water_fee = float(data['water_fee']) if data.get('water_fee') else 0
        electricity_fee = float(data['electricity_fee']) if data.get('electricity_fee') else 0

        # 从费用反推用量
        water_usage = water_fee / 3.5 if water_fee > 0 else 0
        electricity_usage = electricity_fee / 1.2 if electricity_fee > 0 else 0

        rental.room_number = data['room_number']
        rental.tenant_name = data['tenant_name']
        rental.deposit = float(data['deposit']) if data.get('deposit') else 0
        rental.monthly_rent = float(data['monthly_rent']) if data.get('monthly_rent') else 0
        rental.water_fee = water_fee
        rental.water_usage = water_usage
        rental.electricity_usage = electricity_usage
        rental.electricity_fee = electricity_fee
        rental.utilities_fee = float(data['utilities_fee']) if data.get('utilities_fee') else 0
        rental.total_due = float(data['total_due']) if data.get('total_due') else 0
        rental.payment_status = int(data['payment_status']) if data.get('payment_status') else 2
        rental.check_in_date = check_in_date
        rental.check_out_date = check_out_date
        rental.contract_start_date = contract_start_date
        rental.contract_end_date = contract_end_date
        rental.remarks = data.get('remarks', '')

        db.session.commit()
        return jsonify({'success': True, 'message': '租房管理更新成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


# 标记已缴费
@app.route('/rental/<int:rental_id>/mark_paid', methods=['POST'])
def mark_rental_paid(rental_id):
    """标记租房记录为已缴费"""
    try:
        rental = RentalOld.query.get_or_404(rental_id)

        # 更新缴费状态为已缴费(1)
        rental.payment_status = 1
        rental.updated_at = datetime.now()

        # 创建缴费记录到 rental_records_old 表
        rental_record = RentalRecordsOld(
            room_number=rental.room_number,
            tenant_name=rental.tenant_name,
            total_rent=rental.total_due,  # 使用应缴费总额
            payment_date=datetime.now().date(),
            created_at=datetime.now()
        )

        # 保存更新和新记录
        db.session.add(rental_record)
        db.session.commit()

        return jsonify({'success': True, 'message': '已成功标记为已缴费并记录缴费信息'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'标记失败: {str(e)}'})


# 删除租房管理
@app.route('/api/rental_old/<int:rental_id>', methods=['DELETE'])
def api_delete_rental_old(rental_id):
    """删除租房管理记录"""
    try:
        rental = RentalOld.query.get_or_404(rental_id)

        # 删除租房记录
        db.session.delete(rental)
        db.session.commit()
        return jsonify({'success': True, 'message': '租房记录删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 六楼租房管理API
@app.route('/api/rental_new', methods=['POST'])
def api_add_rental_new():
    """添加六楼租房管理记录"""
    try:
        data = request.get_json()

        # 检查房号是否已存在
        existing_rental = RentalNew.query.filter_by(room_number=data['room_number']).first()
        if existing_rental:
            return jsonify({'success': False, 'message': '该房号已有租房记录'})

        # 处理日期字段
        check_in_date = None
        check_out_date = None
        contract_start_date = None
        contract_end_date = None

        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        if data.get('check_out_date'):
            try:
                check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '退房日期格式不正确'})

        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        # 计算应缴费总额
        monthly_rent = float(data.get('monthly_rent', 0))
        water_fee = float(data.get('water_fee', 0))
        electricity_fee = float(data.get('electricity_fee', 0))
        utilities_fee = float(data.get('utilities_fee', 0))

        # 从费用反推用量（前端已经计算好费用，我们需要反推用量）
        water_usage = water_fee / 3.5 if water_fee > 0 else 0  # 水费：3.5元/方
        electricity_usage = electricity_fee / 1.2 if electricity_fee > 0 else 0  # 电费：1.2元/度

        total_due = monthly_rent + utilities_fee

        # 创建新记录
        new_rental = RentalNew(
            room_number=data['room_number'],
            tenant_name=data['tenant_name'],
            deposit=float(data.get('deposit', 0)),
            monthly_rent=monthly_rent,
            water_fee=water_fee,
            electricity_fee=electricity_fee,
            water_usage=water_usage,
            electricity_usage=electricity_usage,
            utilities_fee=utilities_fee,
            total_due=total_due,
            payment_status=int(data.get('payment_status', 2)),  # 默认未缴费
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            remarks=data.get('remarks', '')
        )

        db.session.add(new_rental)
        db.session.commit()

        return jsonify({'success': True, 'message': '租房记录添加成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})


@app.route('/api/rental_new/<int:rental_id>', methods=['GET'])
def api_get_rental_new(rental_id):
    """六楼租房管理详情"""
    try:
        rental = RentalNew.query.get_or_404(rental_id)
        status_map = {
            1: '已缴费',
            2: '未缴费'
        }

        rental_data = {
            'id': rental.id,
            'room_number': rental.room_number,
            'tenant_name': rental.tenant_name,
            'deposit': float(rental.deposit) if rental.deposit else 0,
            'monthly_rent': float(rental.monthly_rent) if rental.monthly_rent else 0,
            'water_fee': float(rental.water_fee) if rental.water_fee else 0,
            'electricity_fee': float(rental.electricity_fee) if rental.electricity_fee else 0,
            'water_usage': float(rental.water_usage) if hasattr(rental, 'water_usage') and rental.water_usage else 0,
            'electricity_usage': float(rental.electricity_usage) if hasattr(rental,
                                                                            'electricity_usage') and rental.electricity_usage else 0,
            'utilities_fee': float(rental.utilities_fee) if rental.utilities_fee else 0,
            'total_due': float(rental.total_due) if rental.total_due else 0,
            'payment_status': rental.payment_status,
            'payment_status_text': status_map.get(rental.payment_status, '未知'),
            'check_in_date': rental.check_in_date.strftime('%Y-%m-%d') if rental.check_in_date else '',
            'check_out_date': rental.check_out_date.strftime('%Y-%m-%d') if rental.check_out_date else '',
            'contract_start_date': rental.contract_start_date.strftime(
                '%Y-%m-%d') if rental.contract_start_date else '',
            'contract_end_date': rental.contract_end_date.strftime('%Y-%m-%d') if rental.contract_end_date else '',
            'remarks': rental.remarks or '',
            'created_at': rental.created_at.strftime('%Y-%m-%d %H:%M:%S') if rental.created_at else '-',
            'updated_at': rental.updated_at.strftime('%Y-%m-%d %H:%M:%S') if rental.updated_at else '-'
        }

        return jsonify(rental_data)
    except Exception as e:
        return jsonify({'error': f'获取租房管理失败: {str(e)}'})


@app.route('/api/rental_new/<int:rental_id>', methods=['PUT'])
def api_update_rental_new(rental_id):
    """更新六楼租房管理"""
    try:
        rental = RentalNew.query.get_or_404(rental_id)
        data = request.get_json()

        # 检查房号是否被其他记录使用
        if data['room_number'] != rental.room_number:
            existing_info = RentalNew.query.filter_by(room_number=data['room_number']).first()
            if existing_info:
                return jsonify({'success': False, 'message': '该房号已有其他租房管理'})

        # 处理入住日期
        check_in_date = None
        if data.get('check_in_date'):
            try:
                check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '入住日期格式不正确'})

        # 处理合同开始日期
        contract_start_date = None
        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        # 处理合同结束日期
        contract_end_date = None
        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        # 处理退房日期
        check_out_date = None
        if data.get('check_out_date'):
            try:
                check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '退房日期格式不正确'})

        # 获取费用数据
        water_fee = float(data['water_fee']) if data.get('water_fee') else 0
        electricity_fee = float(data['electricity_fee']) if data.get('electricity_fee') else 0

        # 从费用反推用量
        water_usage = water_fee / 3.5 if water_fee > 0 else 0
        electricity_usage = electricity_fee / 1.2 if electricity_fee > 0 else 0

        rental.room_number = data['room_number']
        rental.tenant_name = data['tenant_name']
        rental.deposit = float(data['deposit']) if data.get('deposit') else 0
        rental.monthly_rent = float(data['monthly_rent']) if data.get('monthly_rent') else 0
        rental.water_fee = water_fee
        rental.water_usage = water_usage
        rental.electricity_usage = electricity_usage
        rental.electricity_fee = electricity_fee
        rental.utilities_fee = float(data['utilities_fee']) if data.get('utilities_fee') else 0
        rental.total_due = float(data['total_due']) if data.get('total_due') else 0
        rental.payment_status = int(data['payment_status']) if data.get('payment_status') else 2
        rental.check_in_date = check_in_date
        rental.check_out_date = check_out_date
        rental.contract_start_date = contract_start_date
        rental.contract_end_date = contract_end_date
        rental.remarks = data.get('remarks', '')

        db.session.commit()
        return jsonify({'success': True, 'message': '租房管理更新成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/rental_new/<int:rental_id>/mark_paid', methods=['POST'])
def mark_rental_new_paid(rental_id):
    """标记六楼租房记录为已缴费"""
    try:
        rental = RentalNew.query.get_or_404(rental_id)

        # 更新缴费状态为已缴费(1)
        rental.payment_status = 1
        rental.updated_at = datetime.now()

        # 同时更新 rental_info_new 表中对应房间的缴费状态
        rental_info = RentalInfoNew.query.filter_by(room_number=rental.room_number).first()
        if rental_info:
            rental_info.rental_status = 1  # 标记为已缴费
            rental_info.updated_at = datetime.now()

        # 创建缴费记录到 rental_records_new 表
        rental_record = RentalRecordsNew(
            room_number=rental.room_number,
            tenant_name=rental.tenant_name,
            total_rent=rental.total_due,  # 使用应缴费总额
            payment_date=datetime.now().date(),
            created_at=datetime.now()
        )

        # 保存更新和新记录
        db.session.add(rental_record)
        db.session.commit()

        return jsonify({'success': True, 'message': '已成功标记为已缴费并记录缴费信息'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'标记失败: {str(e)}'})


@app.route('/api/rental_new/<int:rental_id>', methods=['DELETE'])
def api_delete_rental_new(rental_id):
    """删除六楼租房管理记录"""
    try:
        rental = RentalNew.query.get_or_404(rental_id)

        # 删除租房记录
        db.session.delete(rental)
        db.session.commit()
        return jsonify({'success': True, 'message': '租房记录删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 合同管理API
@app.route('/api/contracts_old/<int:contract_id>', methods=['GET'])
def api_get_contract_old(contract_id):
    """获取合同详情"""
    try:
        contract = ContractsOld.query.get_or_404(contract_id)

        status_map = {
            1: '有效',
            2: '失效'
        }

        utilities_map = {
            1: '包含',
            2: '不包含'
        }

        # 安全的日期格式化函数
        def safe_date_format(date_obj, format_str='%Y-%m-%d'):
            if date_obj is None:
                return ''
            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime(format_str)
            else:
                return str(date_obj)

        def safe_datetime_format(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
            if datetime_obj is None:
                return '-'
            if hasattr(datetime_obj, 'strftime'):
                return datetime_obj.strftime(format_str)
            else:
                return str(datetime_obj)

        contract_data = {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'room_number': contract.room_number,
            'tenant_name': contract.tenant_name,
            'tenant_phone': contract.tenant_phone,
            'tenant_id_card': contract.tenant_id_card,
            'landlord_name': contract.landlord_name,
            'landlord_phone': contract.landlord_phone,
            'monthly_rent': float(contract.monthly_rent),
            'deposit': float(contract.deposit),
            'contract_start_date': safe_date_format(contract.contract_start_date),
            'contract_end_date': safe_date_format(contract.contract_end_date),
            'contract_duration': contract.contract_duration,
            'payment_method': contract.payment_method,
            'rent_due_date': safe_date_format(contract.rent_due_date),
            'contract_status': contract.contract_status,
            'contract_status_text': status_map.get(contract.contract_status, '未知'),
            'utilities_included': contract.utilities_included,
            'utilities_included_text': utilities_map.get(contract.utilities_included, '未知'),
            'water_rate': float(contract.water_rate),
            'electricity_rate': float(contract.electricity_rate),
            'contract_terms': contract.contract_terms or '',
            'special_agreement': contract.special_agreement or '',
            'remarks': contract.remarks or '',
            'created_at': safe_datetime_format(contract.created_at),
            'updated_at': safe_datetime_format(contract.updated_at)
        }

        return jsonify({'success': True, 'contract': contract_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取合同信息失败: {str(e)}'})


@app.route('/api/contracts_old/<int:contract_id>', methods=['PUT'])
def api_update_contract_old(contract_id):
    """更新合同信息"""
    try:
        contract = ContractsOld.query.get_or_404(contract_id)
        data = request.get_json()

        # 检查合同编号是否被其他合同使用
        if data['contract_number'] != contract.contract_number:
            existing_contract = ContractsOld.query.filter_by(contract_number=data['contract_number']).first()
            if existing_contract:
                return jsonify({'success': False, 'message': '合同编号已存在'})

        # 处理日期字段
        contract_start_date = None
        contract_end_date = None
        rent_due_date = None

        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        if data.get('rent_due_date'):
            try:
                rent_due_date = datetime.strptime(data['rent_due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '租金到期日期格式不正确'})

        # 更新合同信息
        contract.contract_number = data['contract_number']
        contract.room_number = data['room_number']
        contract.tenant_name = data['tenant_name']
        contract.tenant_phone = data['tenant_phone']
        contract.tenant_id_card = data['tenant_id_card']
        contract.landlord_name = data['landlord_name']
        contract.landlord_phone = data['landlord_phone']
        contract.monthly_rent = float(data['monthly_rent'])
        contract.deposit = float(data['deposit'])
        contract.contract_start_date = contract_start_date
        contract.contract_end_date = contract_end_date
        contract.contract_duration = int(data['contract_duration'])
        contract.payment_method = data['payment_method']
        contract.rent_due_date = rent_due_date
        contract.contract_status = int(data['contract_status'])
        contract.utilities_included = int(data['utilities_included'])
        contract.water_rate = float(data['water_rate'])
        contract.electricity_rate = float(data['electricity_rate'])
        contract.contract_terms = data.get('contract_terms', '')
        contract.special_agreement = data.get('special_agreement', '')
        contract.remarks = data.get('remarks', '')
        contract.updated_at = datetime.now()

        db.session.commit()
        return jsonify({'success': True, 'message': '合同更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/api/contracts_old/<int:contract_id>/download', methods=['GET'])
def api_download_contract_old(contract_id):
    """下载合同PDF文档"""
    try:
        contract = ContractsOld.query.get_or_404(contract_id)

        # 生成合同PDF内容
        pdf_buffer = generate_contract_pdf(contract)

        # 生成文件名
        filename = f"合同_{contract.contract_number}_{contract.tenant_name}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})


def generate_contract_pdf(contract):
    """生成支持中文的合同PDF内容"""

    # 创建内存缓冲区
    buffer = BytesIO()

    # 注册中文字体
    chinese_font = 'Helvetica'  # 默认字体

    # Windows系统中文字体路径列表
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
        'C:/Windows/Fonts/msyhbd.ttc',  # 微软雅黑粗体
        'C:/Windows/Fonts/simsun.ttc',  # 宋体
        'C:/Windows/Fonts/simhei.ttf',  # 黑体
        'C:/Windows/Fonts/simkai.ttf',  # 楷体
    ]

    # 尝试注册可用的中文字体
    for i, font_path in enumerate(font_paths):
        try:
            if os.path.exists(font_path):
                font_name = f'ChineseFont{i}'
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                chinese_font = font_name
                print(f"成功注册字体: {font_path} -> {font_name}")
                break
        except Exception as e:
            print(f"注册字体失败 {font_path}: {e}")
            continue

    if chinese_font == 'Helvetica':
        print("警告: 未找到可用的中文字体，使用默认字体可能导致中文显示异常")

    # 创建PDF文档
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=60, bottomMargin=60,
                            leftMargin=60, rightMargin=60)

    # 安全的日期格式化函数
    def safe_date_format(date_obj):
        if date_obj is None:
            return '____年____月____日'
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%Y年%m月%d日')
        else:
            return str(date_obj)

    # 状态文本映射
    status_map = {1: '有效', 2: '失效'}
    utilities_map = {1: '包含', 2: '不包含'}

    # 创建样式
    styles = getSampleStyleSheet()

    # 自定义样式（使用中文字体）
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=chinese_font
    )

    heading_style = ParagraphStyle(
        'ChineseHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15,
        fontName=chinese_font
    )

    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6,
        fontName=chinese_font
    )

    # 构建内容
    story = []

    # 标题
    story.append(Paragraph("房屋租赁合同", title_style))
    story.append(Paragraph(f"合同编号：{contract.contract_number}", normal_style))
    story.append(Spacer(1, 20))

    # 一、合同基本信息
    story.append(Paragraph("一、合同基本信息", heading_style))
    basic_data = [
        ['合同编号', str(contract.contract_number), '房间号', str(contract.room_number)],
        ['月租金', f'¥{contract.monthly_rent:.2f}', '押金', f'¥{contract.deposit:.2f}'],
        ['合同状态', status_map.get(contract.contract_status, '未知'),
         '付款方式', str(contract.payment_method or '按月付款')]
    ]
    basic_table = Table(basic_data, colWidths=[70, 110, 70, 110])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 12))

    # 二、租客信息
    story.append(Paragraph("二、租客信息", heading_style))
    tenant_data = [
        ['租客姓名', str(contract.tenant_name), '联系电话', str(contract.tenant_phone or '未填写')],
        ['身份证号', str(contract.tenant_id_card or '未填写'), '', '']
    ]
    tenant_table = Table(tenant_data, colWidths=[70, 110, 70, 110])
    tenant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (1, 1), (3, 1)),  # 合并身份证号的单元格
    ]))
    story.append(tenant_table)
    story.append(Spacer(1, 12))

    # 三、房东信息
    story.append(Paragraph("三、房东信息", heading_style))
    landlord_data = [
        ['房东姓名', str(contract.landlord_name or '未填写'),
         '联系电话', str(contract.landlord_phone or '未填写')]
    ]
    landlord_table = Table(landlord_data, colWidths=[70, 110, 70, 110])
    landlord_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(landlord_table)
    story.append(Spacer(1, 12))

    # 四、合同期限
    story.append(Paragraph("四、合同期限", heading_style))
    period_data = [
        ['合同开始', safe_date_format(contract.contract_start_date),
         '合同结束', safe_date_format(contract.contract_end_date)],
        ['租期时长', f'{contract.contract_duration or 12}个月',
         '租金到期', safe_date_format(contract.rent_due_date)]
    ]
    period_table = Table(period_data, colWidths=[70, 110, 70, 110])
    period_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(period_table)
    story.append(Spacer(1, 12))

    # 五、费用信息
    story.append(Paragraph("五、费用信息", heading_style))
    fee_data = [
        ['水电费', utilities_map.get(contract.utilities_included, '未知'),
         '水费单价', f'¥{contract.water_rate:.2f}/吨'],
        ['电费单价', f'¥{contract.electricity_rate:.2f}/度', '', '']
    ]
    fee_table = Table(fee_data, colWidths=[70, 110, 70, 110])
    fee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(fee_table)
    story.append(Spacer(1, 12))

    # 六、合同条款
    story.append(Paragraph("六、合同条款", heading_style))

    # 处理合同条款文本
    terms_lines = []
    terms_lines.append("1. 基本条款：")
    terms_lines.append(str(contract.contract_terms or '按照国家相关法律法规执行，双方应遵守合同约定。'))
    terms_lines.append("")
    terms_lines.append("2. 特殊约定：")
    terms_lines.append(str(contract.special_agreement or '无特殊约定。'))
    terms_lines.append("")
    terms_lines.append("3. 备注说明：")
    terms_lines.append(str(contract.remarks or '无备注。'))

    for line in terms_lines:
        if line.strip():
            story.append(Paragraph(line, normal_style))
        else:
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 20))

    # 签名区域
    signature_data = [
        ['甲方（房东）', '乙方（租客）'],
        ['', ''],
        ['', ''],
        ['签名：______________', '签名：______________'],
        [f'签署日期：{safe_date_format(contract.created_at.date() if contract.created_at else None)}',
         f'签署日期：{safe_date_format(contract.created_at.date() if contract.created_at else None)}']
    ]
    signature_table = Table(signature_data, colWidths=[180, 180])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(signature_table)
    story.append(Spacer(1, 15))

    # 页脚
    footer_lines = [
        "本合同一式两份，甲乙双方各执一份，具有同等法律效力。",
        f"合同生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"
    ]

    footer_style = ParagraphStyle(
        'ChineseFooter',
        parent=normal_style,
        alignment=TA_CENTER,
        fontSize=8
    )

    for line in footer_lines:
        story.append(Paragraph(line, footer_style))

    # 构建PDF
    doc.build(story)

    # 返回缓冲区
    buffer.seek(0)
    return buffer


@app.route('/api/contracts_old', methods=['POST'])
def api_create_contract_old():
    """创建五楼合同"""
    try:
        data = request.get_json()

        # 检查合同编号是否已存在
        existing_contract = ContractsOld.query.filter_by(contract_number=data['contract_number']).first()
        if existing_contract:
            return jsonify({'success': False, 'message': '合同编号已存在'})

        # 处理日期字段
        sign_date = None
        start_date = None
        end_date = None

        if data.get('sign_date'):
            try:
                sign_date = datetime.strptime(data['sign_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '签约日期格式不正确'})

        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '租期开始日期格式不正确'})

        if data.get('end_date'):
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '租期结束日期格式不正确'})

        # 创建新合同
        new_contract = ContractsOld(
            contract_number=data['contract_number'],
            room_number=data.get('room_number', ''),
            tenant_name=data['tenant_name'],
            tenant_phone=data.get('tenant_phone', ''),
            tenant_id_card=data.get('tenant_id_card', ''),
            landlord_name=data.get('landlord_name', ''),
            landlord_phone=data.get('landlord_phone', ''),
            monthly_rent=float(data['monthly_rent']),
            deposit=float(data.get('deposit', 0)),
            contract_start_date=start_date,
            contract_end_date=end_date,
            contract_duration=int(data.get('contract_duration', 12)),
            payment_method=data.get('payment_cycle', '按月付款'),
            rent_due_date=start_date,
            contract_status=1,
            utilities_included=int(data.get('include_utilities', 2)),
            water_rate=float(data.get('water_rate', 0)),
            electricity_rate=float(data.get('electricity_rate', 0)),
            contract_terms='',
            special_agreement='',
            remarks=data.get('notes', ''),
            created_at=sign_date or datetime.now().date(),
            updated_at=datetime.now()
        )

        db.session.add(new_contract)
        db.session.commit()
        return jsonify({'success': True, 'message': '合同创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})


@app.route('/api/contracts_old/<int:contract_id>', methods=['DELETE'])
def api_delete_contract_old(contract_id):
    """删除五楼合同"""
    try:
        contract = ContractsOld.query.get_or_404(contract_id)
        db.session.delete(contract)
        db.session.commit()
        return jsonify({'success': True, 'message': '合同删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


# 六楼合同管理API
@app.route('/api/contracts_new/<int:contract_id>', methods=['GET'])
def api_get_contract_new(contract_id):
    """获取六楼合同详情"""
    try:
        contract = ContractsNew.query.get_or_404(contract_id)

        status_map = {
            1: '有效',
            2: '失效'
        }

        utilities_map = {
            1: '包含',
            2: '不包含'
        }

        # 安全的日期格式化函数
        def safe_date_format(date_obj, format_str='%Y-%m-%d'):
            if date_obj is None:
                return ''
            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime(format_str)
            else:
                return str(date_obj)

        def safe_datetime_format(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
            if datetime_obj is None:
                return '-'
            if hasattr(datetime_obj, 'strftime'):
                return datetime_obj.strftime(format_str)
            else:
                return str(datetime_obj)

        contract_data = {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'room_number': contract.room_number,
            'tenant_name': contract.tenant_name,
            'tenant_phone': contract.tenant_phone,
            'tenant_id_card': contract.tenant_id_card,
            'landlord_name': contract.landlord_name,
            'landlord_phone': contract.landlord_phone,
            'monthly_rent': float(contract.monthly_rent),
            'deposit': float(contract.deposit),
            'contract_start_date': safe_date_format(contract.contract_start_date),
            'contract_end_date': safe_date_format(contract.contract_end_date),
            'contract_duration': contract.contract_duration,
            'payment_method': contract.payment_method,
            'rent_due_date': safe_date_format(contract.rent_due_date),
            'contract_status': contract.contract_status,
            'contract_status_text': status_map.get(contract.contract_status, '未知'),
            'utilities_included': contract.utilities_included,
            'utilities_included_text': utilities_map.get(contract.utilities_included, '未知'),
            'water_rate': float(contract.water_rate),
            'electricity_rate': float(contract.electricity_rate),
            'contract_terms': contract.contract_terms or '',
            'special_agreement': contract.special_agreement or '',
            'remarks': contract.remarks or '',
            'created_at': safe_datetime_format(contract.created_at),
            'updated_at': safe_datetime_format(contract.updated_at)
        }

        return jsonify({'success': True, 'contract': contract_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取合同信息失败: {str(e)}'})


@app.route('/api/contracts_new/<int:contract_id>', methods=['PUT'])
def api_update_contract_new(contract_id):
    """更新六楼合同信息"""
    try:
        contract = ContractsNew.query.get_or_404(contract_id)
        data = request.get_json()

        # 检查合同编号是否被其他合同使用
        if data['contract_number'] != contract.contract_number:
            existing_contract = ContractsNew.query.filter_by(contract_number=data['contract_number']).first()
            if existing_contract:
                return jsonify({'success': False, 'message': '合同编号已存在'})

        # 处理日期字段
        contract_start_date = None
        contract_end_date = None
        rent_due_date = None

        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        if data.get('rent_due_date'):
            try:
                rent_due_date = datetime.strptime(data['rent_due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '租金到期日期格式不正确'})

        # 更新合同信息
        contract.contract_number = data['contract_number']
        contract.room_number = data['room_number']
        contract.tenant_name = data['tenant_name']
        contract.tenant_phone = data.get('tenant_phone', '')
        contract.tenant_id_card = data.get('tenant_id_card', '')
        contract.landlord_name = data['landlord_name']
        contract.landlord_phone = data.get('landlord_phone', '')
        contract.monthly_rent = float(data['monthly_rent'])
        contract.deposit = float(data['deposit'])
        contract.contract_start_date = contract_start_date
        contract.contract_end_date = contract_end_date
        contract.contract_duration = int(data.get('contract_duration', 12))
        contract.payment_method = data.get('payment_method', '月付')
        contract.rent_due_date = rent_due_date
        contract.contract_status = int(data.get('contract_status', 1))
        contract.utilities_included = int(data.get('utilities_included', 2))
        contract.water_rate = float(data.get('water_rate', 0))
        contract.electricity_rate = float(data.get('electricity_rate', 0))
        contract.contract_terms = data.get('contract_terms', '')
        contract.special_agreement = data.get('special_agreement', '')
        contract.remarks = data.get('remarks', '')
        contract.updated_at = datetime.now()

        db.session.commit()
        return jsonify({'success': True, 'message': '合同更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/api/contracts_new/<int:contract_id>', methods=['DELETE'])
def api_delete_contract_new(contract_id):
    """删除六楼合同"""
    try:
        contract = ContractsNew.query.get_or_404(contract_id)
        db.session.delete(contract)
        db.session.commit()
        return jsonify({'success': True, 'message': '合同删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@app.route('/api/contracts_new', methods=['POST'])
def api_create_contract_new():
    """创建六楼合同"""
    try:
        data = request.get_json()

        # 检查合同编号是否已存在
        existing_contract = ContractsNew.query.filter_by(contract_number=data['contract_number']).first()
        if existing_contract:
            return jsonify({'success': False, 'message': '合同编号已存在'})

        # 处理日期字段
        contract_start_date = None
        contract_end_date = None

        if data.get('contract_start_date'):
            try:
                contract_start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同开始日期格式不正确'})

        if data.get('contract_end_date'):
            try:
                contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '合同结束日期格式不正确'})

        # 创建新合同
        new_contract = ContractsNew(
            contract_number=data['contract_number'],
            room_number=data['room_number'],
            tenant_name=data['tenant_name'],
            tenant_phone=data.get('tenant_phone', ''),
            tenant_id_card=data.get('tenant_id_card', ''),
            landlord_name=data['landlord_name'],
            landlord_phone=data.get('landlord_phone', ''),
            monthly_rent=float(data['monthly_rent']),
            deposit=float(data['deposit']),
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            contract_duration=int(data.get('contract_duration', 12)),
            payment_method=data.get('payment_method', '月付'),
            rent_due_date=contract_start_date,
            contract_status=1,
            utilities_included=int(data.get('utilities_included', 2)),
            water_rate=float(data.get('water_rate', 0)),
            electricity_rate=float(data.get('electricity_rate', 0)),
            contract_terms=data.get('contract_terms', ''),
            special_agreement=data.get('special_agreement', ''),
            remarks=data.get('remarks', ''),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_contract)
        db.session.commit()
        return jsonify({'success': True, 'message': '合同创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})


@app.route('/api/contracts_new/<int:contract_id>/download', methods=['GET'])
def api_download_contract_new(contract_id):
    """下载六楼合同PDF文档"""
    try:
        contract = ContractsNew.query.get_or_404(contract_id)

        # 生成合同PDF内容
        pdf_buffer = generate_contract_pdf(contract)

        # 生成文件名
        filename = f"合同_{contract.contract_number}_{contract.tenant_name}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})


# 旧版系统设置
@app.route('/system_setting')
def system_setting():
    """系统设置页面"""
    return render_template('system_setting.html')


# 新版本的系统设置
@app.route('/system_setting_new')
def system_setting_new():
    """系统设置页面（新版）"""
    return render_template('system_setting_new.html')


# 退出系统页面
@app.route('/out_system')
def out_system():
    """退出系统页面"""
    # 检查登录状态
    if 'admin_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))

    return render_template('out_system.html')


# 获取已出租房间列表API
@app.route('/api/rented_rooms_old', methods=['GET'])
def api_get_rented_rooms_old():
    """获取五楼已出租房间列表"""
    try:
        # 查询状态为已出租(2)的房间，并关联租房信息获取租客姓名
        rented_rooms = db.session.query(RoomsOld, RentalInfoOld).join(
            RentalInfoOld, RoomsOld.room_number == RentalInfoOld.room_number
        ).filter(RoomsOld.room_status == 2).all()

        rooms_list = []
        for room, rental_info in rented_rooms:
            rooms_list.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'base_rent': float(room.base_rent) if room.base_rent else 0,
                'deposit': float(room.deposit) if room.deposit else 0,  # 使用房间表的押金
                'tenant_name': rental_info.tenant_name if rental_info else '',
                'tenant_phone': rental_info.phone if rental_info else '',
                'rental_deposit': float(rental_info.deposit) if rental_info and rental_info.deposit else 0,  # 租房信息表的押金
                'check_in_date': rental_info.check_in_date.strftime(
                    '%Y-%m-%d') if rental_info and rental_info.check_in_date else ''
            })

        return jsonify({
            'success': True,
            'rooms': rooms_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取已出租房间失败: {str(e)}'
        })


@app.route('/api/rented_rooms_new', methods=['GET'])
def api_get_rented_rooms_new():
    """获取六楼已出租房间列表"""
    try:
        # 查询状态为已出租(2)的房间，并关联租房信息获取租客姓名
        rented_rooms = db.session.query(RoomsNew, RentalInfoNew).join(
            RentalInfoNew, RoomsNew.room_number == RentalInfoNew.room_number
        ).filter(RoomsNew.room_status == 2).all()

        rooms_list = []
        for room, rental_info in rented_rooms:
            rooms_list.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'base_rent': float(room.base_rent) if room.base_rent else 0,
                'deposit': float(room.deposit) if room.deposit else 0,  # 使用房间表的押金
                'tenant_name': rental_info.tenant_name if rental_info else '',
                'tenant_phone': rental_info.phone if rental_info else '',
                'rental_deposit': float(rental_info.deposit) if rental_info and rental_info.deposit else 0,  # 租房信息表的押金
                'check_in_date': rental_info.check_in_date.strftime(
                    '%Y-%m-%d') if rental_info and rental_info.check_in_date else ''
            })

        return jsonify({
            'success': True,
            'rooms': rooms_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取已出租房间失败: {str(e)}'
        })


# 获取空闲房间列表API
@app.route('/api/available_rooms_old', methods=['GET'])
def api_get_available_rooms_old():
    """获取五楼空闲房间列表"""
    try:
        # 查询状态为空闲(1)的房间
        available_rooms = RoomsOld.query.filter_by(room_status=1).all()

        rooms_list = []
        for room in available_rooms:
            rooms_list.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'base_rent': float(room.base_rent) if room.base_rent else 0
            })

        return jsonify({
            'success': True,
            'rooms': rooms_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取空闲房间失败: {str(e)}'
        })


@app.route('/api/available_rooms_new', methods=['GET'])
def api_get_available_rooms_new():
    """获取六楼空闲房间列表"""
    try:
        # 查询状态为空闲(1)的房间
        available_rooms = RoomsNew.query.filter_by(room_status=1).all()

        rooms_list = []
        for room in available_rooms:
            rooms_list.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'base_rent': float(room.base_rent) if room.base_rent else 0
            })

        return jsonify({
            'success': True,
            'rooms': rooms_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取空闲房间失败: {str(e)}'
        })


@app.route('/admin')
def admin():
    admin_list = Admin.query.all()
    return render_template('admin_list.html', admin_list=admin_list)


# 管理员API接口
@app.route('/api/admin', methods=['POST'])
def api_create_admin():
    """创建新管理员"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('admin_name') or not data.get('password'):
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        admin_name = data['admin_name'].strip()
        password = data['password']
        
        # 验证用户名长度
        if len(admin_name) < 3:
            return jsonify({'success': False, 'message': '用户名长度至少3位'})
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6位'})
        
        # 检查用户名是否已存在
        existing_admin = Admin.query.filter_by(admin_name=admin_name).first()
        if existing_admin:
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 创建新管理员
        new_admin = Admin(admin_name=admin_name)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '管理员创建成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})


@app.route('/api/admin/<int:admin_id>', methods=['GET'])
def api_get_admin(admin_id):
    """获取管理员详情"""
    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({'error': '管理员不存在'})
        
        return jsonify({
            'id': admin.id,
            'admin_name': admin.admin_name,
            'last_login': admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else None
        })
        
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'})


@app.route('/api/admin/<int:admin_id>', methods=['PUT'])
def api_update_admin(admin_id):
    """更新管理员信息"""
    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({'success': False, 'message': '管理员不存在'})
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('admin_name'):
            return jsonify({'success': False, 'message': '用户名不能为空'})
        
        admin_name = data['admin_name'].strip()
        
        # 验证用户名长度
        if len(admin_name) < 3:
            return jsonify({'success': False, 'message': '用户名长度至少3位'})
        
        # 检查用户名是否已被其他管理员使用
        existing_admin = Admin.query.filter(
            Admin.admin_name == admin_name,
            Admin.id != admin_id
        ).first()
        if existing_admin:
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 更新用户名
        admin.admin_name = admin_name
        
        # 如果提供了新密码，则更新密码
        if data.get('password'):
            password = data['password']
            if len(password) < 6:
                return jsonify({'success': False, 'message': '密码长度至少6位'})
            admin.set_password(password)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '管理员信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/api/admin/<int:admin_id>', methods=['DELETE'])
def api_delete_admin(admin_id):
    """删除管理员"""
    try:
        # 检查管理员总数，确保至少保留一个管理员
        total_admins = Admin.query.count()
        if total_admins <= 1:
            return jsonify({'success': False, 'message': '系统至少需要保留一个管理员账户'})
        
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({'success': False, 'message': '管理员不存在'})
        
        db.session.delete(admin)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '管理员删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@app.route('/mobile-test')
def mobile_test():
    """移动端适配测试页面"""
    return render_template('mobile-test.html')

@app.route('/mobile-table-test')
def mobile_table_test():
    """移动端表格滚动测试页面"""
    return render_template('mobile-table-test.html')


@app.route('/debug-login')
def debug_login():
    """登录问题调试页面"""
    try:
        from models import Admin
        from werkzeug.security import generate_password_hash
        
        # 检查数据库连接
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = "✅ 数据库连接正常"
        except Exception as e:
            db_status = f"❌ 数据库连接失败: {str(e)}"
        
        # 检查Admin表和账户
        try:
            admin_count = Admin.query.count()
            admins = Admin.query.all()
            
            admin_list = []
            for admin in admins:
                # 测试常用密码
                test_passwords = ['123456', 'admin123', 'admin', 'password']
                correct_password = None
                
                for pwd in test_passwords:
                    try:
                        if admin.check_password(pwd):
                            correct_password = pwd
                            break
                    except:
                        pass
                
                admin_list.append({
                    'id': admin.id,
                    'username': admin.admin_name,
                    'has_password': bool(admin.password),
                    'password_hash_length': len(admin.password) if admin.password else 0,
                    'last_login': admin.last_login,
                    'correct_password': correct_password
                })
            
            admin_status = f"✅ 找到 {admin_count} 个管理员账户"
            
        except Exception as e:
            admin_status = f"❌ 查询管理员失败: {str(e)}"
            admin_list = []
        
        # 生成HTML调试页面
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>登录问题调试</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
                .admin-card {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; }}
                .btn {{ background: #007bff; color: white; padding: 8px 16px; text-decoration: none; 
                       border-radius: 4px; display: inline-block; margin: 5px; }}
                .btn-success {{ background: #28a745; }}
                .btn-warning {{ background: #ffc107; color: #212529; }}
                .btn-danger {{ background: #dc3545; }}
                pre {{ background: #f8f9fa; padding: 15px; border: 1px solid #e9ecef; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 登录问题调试页面</h1>
                
                <h2>1. 数据库状态</h2>
                <div class="status {'success' if '✅' in db_status else 'error'}">
                    {db_status}
                </div>
                
                <h2>2. 管理员账户状态</h2>
                <div class="status {'success' if '✅' in admin_status else 'error'}">
                    {admin_status}
                </div>
                
                <h2>3. 管理员账户详情</h2>
        """
        
        if admin_list:
            for admin in admin_list:
                html += f"""
                <div class="admin-card">
                    <h4>👤 用户: {admin['username']}</h4>
                    <p><strong>ID:</strong> {admin['id']}</p>
                    <p><strong>密码状态:</strong> {'✅ 已设置' if admin['has_password'] else '❌ 未设置'}</p>
                    <p><strong>密码哈希长度:</strong> {admin['password_hash_length']} 字符</p>
                    <p><strong>最后登录:</strong> {admin['last_login'] or '从未登录'}</p>
                    <p><strong>测试结果:</strong> 
                        {'✅ 密码: ' + admin['correct_password'] if admin['correct_password'] else '❌ 未找到匹配密码'}
                    </p>
                </div>
                """
        else:
            html += '<div class="status error">❌ 没有找到任何管理员账户</div>'
        
        html += f"""
                <h2>4. 快速操作</h2>
                <a href="/reset-admin-password" class="btn btn-warning">🔧 重置admin密码为123456</a>
                <a href="/create-default-admin" class="btn btn-success">➕ 创建默认管理员</a>
                <a href="/login" class="btn">🏠 返回登录页</a>
                
                <h2>5. 常用登录信息</h2>
                <div class="info status">
                    <h4>默认登录信息:</h4>
                    <p><strong>用户名:</strong> admin</p>
                    <p><strong>密码:</strong> 123456 或 admin123</p>
                </div>
                
                <h2>6. 如何解决登录问题</h2>
                <div class="info status">
                    <ol>
                        <li>如果没有管理员账户，点击"创建默认管理员"</li>
                        <li>如果有账户但密码不对，点击"重置admin密码"</li>
                        <li>如果数据库连接失败，检查数据库配置</li>
                        <li>如果表不存在，访问 <a href="/setup_database">/setup_database</a></li>
                    </ol>
                </div>
                
                <h2>7. 当前应用配置</h2>
                <pre>
数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')[:50]}...
调试模式: {app.debug}
密钥配置: {'已配置' if app.config.get('SECRET_KEY') else '未配置'}
                </pre>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; margin: 20px;">
            <h1>❌ 调试失败</h1>
            <p>错误信息: {str(e)}</p>
            <p>请检查系统配置或查看控制台日志</p>
            <a href="/login">返回登录页</a>
        </body>
        </html>
        """


@app.route('/reset-admin-password')
def reset_admin_password():
    """重置管理员密码"""
    try:
        from models import Admin
        
        # 查找或创建admin用户
        admin = Admin.query.filter_by(admin_name='admin').first()
        
        if not admin:
            # 创建admin用户
            admin = Admin(admin_name='admin')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            
            return f"""
            <html>
            <body style="font-family: Arial; margin: 20px;">
                <h1>✅ 管理员账户创建成功</h1>
                <p><strong>用户名:</strong> admin</p>
                <p><strong>密码:</strong> 123456</p>
                <p><a href="/login">立即登录</a> | <a href="/debug-login">返回调试页</a></p>
            </body>
            </html>
            """
        else:
            # 重置密码
            admin.set_password('123456')
            admin.last_login = None
            db.session.commit()
            
            return f"""
            <html>
            <body style="font-family: Arial; margin: 20px;">
                <h1>✅ 密码重置成功</h1>
                <p><strong>用户名:</strong> admin</p>
                <p><strong>新密码:</strong> 123456</p>
                <p><a href="/login">立即登录</a> | <a href="/debug-login">返回调试页</a></p>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; margin: 20px;">
            <h1>❌ 重置失败</h1>
            <p>错误: {str(e)}</p>
            <p><a href="/debug-login">返回调试页</a></p>
        </body>
        </html>
        """


@app.route('/create-default-admin')
def create_default_admin():
    """创建默认管理员账户"""
    try:
        from models import Admin
        
        # 检查是否已存在
        existing = Admin.query.filter_by(admin_name='admin').first()
        if existing:
            return f"""
            <html>
            <body style="font-family: Arial; margin: 20px;">
                <h1>⚠️ 管理员已存在</h1>
                <p>用户名 'admin' 已存在</p>
                <p>如需重置密码，请使用<a href="/reset-admin-password">重置密码功能</a></p>
                <p><a href="/debug-login">返回调试页</a></p>
            </body>
            </html>
            """
        
        # 创建默认管理员
        admin = Admin(admin_name='admin')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()
        
        return f"""
        <html>
        <body style="font-family: Arial; margin: 20px;">
            <h1>✅ 默认管理员创建成功</h1>
            <p><strong>用户名:</strong> admin</p>
            <p><strong>密码:</strong> 123456</p>
            <p><a href="/login">立即登录</a> | <a href="/debug-login">返回调试页</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; margin: 20px;">
            <h1>❌ 创建失败</h1>
            <p>错误: {str(e)}</p>
            <p><a href="/debug-login">返回调试页</a></p>
        </body>
        </html>
        """


if __name__ == '__main__':
    with app.app_context():
        try:
            # 测试数据库连接
            db.create_all()
            print("数据库连接成功！")
        except Exception as e:
            print(f"数据库连接失败: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
