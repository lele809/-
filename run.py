from app import app, db

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功！")
        except Exception as e:
            print(f"数据库表创建失败: {e}")

    # 启动应用
    print("启动租房管理系统...")
    print("访问地址: http://127.0.0.1:5002")
    app.run(debug=True, host='127.0.0.1', port=5002)