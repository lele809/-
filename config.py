import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')

    # 数据库配置
    # 优先使用 DATABASE_URL 环境变量（适用于云部署）
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # 云环境：使用 DATABASE_URL
        SQLALCHEMY_DATABASE_URI = database_url
        
        # 兼容性处理 - 确保使用 psycopg 驱动
        if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
            # Render 提供 postgres:// 格式，转换为 postgresql+psycopg://
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql+psycopg://', 1)
        elif SQLALCHEMY_DATABASE_URI.startswith('postgresql://') and '+psycopg' not in SQLALCHEMY_DATABASE_URI:
            # 确保使用 psycopg 驱动而不是默认的 psycopg2
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'postgresql+psycopg://', 1)
            
    elif os.getenv('MYSQL_HOST'):
        # 本地开发环境的MySQL配置
        MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
        MYSQL_USER = os.getenv('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')
        MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'rent_system')
        
        # 构建MySQL连接字符串
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
        
    else:
        # 备用方案：使用 SQLite（用于测试和快速启动）
        import tempfile
        db_path = os.path.join(tempfile.gettempdir(), 'rent_system.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        print(f"⚠️  使用 SQLite 备用数据库: {db_path}")
        print("   请尽快配置正确的数据库连接!")

    # 调试输出（生产环境中可以注释掉）
    print(f"🔧 数据库配置: {SQLALCHEMY_DATABASE_URI.split('@')[0]}@***" if '@' in SQLALCHEMY_DATABASE_URI else f"🔧 数据库配置: {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 10

