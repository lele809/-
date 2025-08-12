from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class ContactsOld(db.Model):
    __tablename__ = 'contacts_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    roomId = db.Column(db.String(20), nullable=False, comment='房间ID')
    phone = db.Column(db.String(20), nullable=False, comment='电话')
    id_card = db.Column(db.String(18), nullable=False, comment='身份证号')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')


class ContactsNew(db.Model):
    __tablename__ = 'contacts_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    roomId = db.Column(db.String(20), nullable=False, comment='房间ID')
    phone = db.Column(db.String(20), nullable=False, comment='电话')
    id_card = db.Column(db.String(18), nullable=False, comment='身份证号')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')


class RentalOld(db.Model):
    __tablename__ = 'rental_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='月租金')
    water_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='水费')
    electricity_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='电费')
    water_usage = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='用水量(方)')
    electricity_usage = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='用电量(度)')
    utilities_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='水电费')
    total_due = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='应缴费')
    payment_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='租赁状态：1=已缴费, 2=未缴费')
    check_in_date = db.Column(db.Date, nullable=True, comment='入住时间')
    check_out_date = db.Column(db.Date, nullable=True, comment='退房时间')
    contract_start_date = db.Column(db.Date, nullable=True, comment='合同开始时间')
    contract_end_date = db.Column(db.Date, nullable=True, comment='合同结束时间')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), comment='更新时间')


class RentalNew(db.Model):
    __tablename__ = 'rental_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='月租金')
    water_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='水费')
    electricity_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='电费')
    water_usage = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='用水量(方)')
    electricity_usage = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='用电量(度)')
    utilities_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='水电费')
    total_due = db.Column(db.Numeric(10, 2), nullable=True, default=0.00, comment='应缴费')
    payment_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='租赁状态：1=已缴费, 2=未缴费')
    check_in_date = db.Column(db.Date, nullable=True, comment='入住时间')
    check_out_date = db.Column(db.Date, nullable=True, comment='退房时间')
    contract_start_date = db.Column(db.Date, nullable=True, comment='合同开始时间')
    contract_end_date = db.Column(db.Date, nullable=True, comment='合同结束时间')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), comment='更新时间')


class RentalRecordsOld(db.Model):
    __tablename__ = 'rental_records_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    total_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='总租金')
    payment_date = db.Column(db.Date, nullable=True, comment='缴费日期')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')


class RentalRecordsNew(db.Model):
    __tablename__ = 'rental_records_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    total_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='总租金')
    payment_date = db.Column(db.Date, nullable=True, comment='缴费日期')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')


class RoomsNew(db.Model):
    __tablename__ = 'rooms_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    room_type = db.Column(db.String(50), nullable=False, comment='房型')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    base_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='基础租金')
    room_status = db.Column(db.SmallInteger, nullable=False, default=1,
                            comment='房间状态：1=空闲, 2=已出租, 3=维修中, 4=停用')
    water_meter_number = db.Column(db.String(50), nullable=False, comment='水表编号')
    electricity_meter_number = db.Column(db.String(50), nullable=False, comment='电表编号')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), comment='更新时间')


class RoomsOld(db.Model):
    __tablename__ = 'rooms_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    room_type = db.Column(db.String(50), nullable=False, comment='房型')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    base_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='基础租金')
    room_status = db.Column(db.SmallInteger, nullable=False, default=1,
                            comment='房间状态：1=空闲, 2=已出租, 3=维修中, 4=停用')
    water_meter_number = db.Column(db.String(50), nullable=False, comment='水表编号')
    electricity_meter_number = db.Column(db.String(50), nullable=False, comment='电表编号')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), comment='更新时间')


class ContractsNew(db.Model):
    __tablename__ = 'contracts_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    contract_number = db.Column(db.String(50), nullable=False, comment='合同编号')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    tenant_phone = db.Column(db.String(20), nullable=False, comment='租客电话')
    tenant_id_card = db.Column(db.String(18), nullable=False, comment='租客身份证号')
    landlord_name = db.Column(db.String(50), nullable=False, comment='房东姓名')
    landlord_phone = db.Column(db.String(20), nullable=False, comment='房东电话')
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='月租金')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    contract_start_date = db.Column(db.Date, nullable=True, comment='合同开始时间')
    contract_end_date = db.Column(db.Date, nullable=True, comment='合同结束时间')
    contract_duration = db.Column(db.Integer, nullable=False, default=0, comment='合同期限')
    payment_method = db.Column(db.String(50), nullable=False, comment='缴费方式')
    rent_due_date = db.Column(db.Date, nullable=True, comment='租金到期日')
    contract_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='合同状态：1=有效, 2=失效')
    utilities_included = db.Column(db.SmallInteger, nullable=False, default=1,
                                   comment='是否包含水电费：1=包含, 2=不包含')
    water_rate = db.Column(db.Numeric(6, 2), nullable=False, default=0.00, comment='水费单价')
    electricity_rate = db.Column(db.Numeric(6, 2), nullable=False, default=0.00, comment='电费单价')
    contract_terms = db.Column(db.Text, nullable=True, comment='合同条款')
    special_agreement = db.Column(db.Text, nullable=True, comment='特殊约定')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='更新时间')


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    admin_name = db.Column(db.String(50), nullable=False, unique=True, comment='管理员用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码哈希')
    last_login = db.Column(db.DateTime, nullable=True, comment='最后登录时间')

    def set_password(self, password):
        """设置密码哈希"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)


class ContractsOld(db.Model):
    __tablename__ = 'contracts_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    contract_number = db.Column(db.String(50), nullable=False, comment='合同编号')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    tenant_phone = db.Column(db.String(20), nullable=False, comment='租客电话')
    tenant_id_card = db.Column(db.String(18), nullable=False, comment='租客身份证号')
    landlord_name = db.Column(db.String(50), nullable=False, comment='房东姓名')
    landlord_phone = db.Column(db.String(20), nullable=False, comment='房东电话')
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='月租金')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    contract_start_date = db.Column(db.Date, nullable=True, comment='合同开始时间')
    contract_end_date = db.Column(db.Date, nullable=True, comment='合同结束时间')
    contract_duration = db.Column(db.Integer, nullable=False, default=0, comment='合同期限')
    payment_method = db.Column(db.String(50), nullable=False, comment='缴费方式')
    rent_due_date = db.Column(db.Date, nullable=True, comment='租金到期日')
    contract_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='合同状态：1=有效, 2=失效')
    utilities_included = db.Column(db.SmallInteger, nullable=False, default=1,
                                   comment='是否包含水电费：1=包含, 2=不包含')
    water_rate = db.Column(db.Numeric(6, 2), nullable=False, default=0.00, comment='水费单价')
    electricity_rate = db.Column(db.Numeric(6, 2), nullable=False, default=0.00, comment='电费单价')
    contract_terms = db.Column(db.Text, nullable=True, comment='合同条款')
    special_agreement = db.Column(db.Text, nullable=True, comment='特殊约定')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='更新时间')


class RentalInfoOld(db.Model):
    __tablename__ = 'rental_info_old'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    phone = db.Column(db.String(20), nullable=False, comment='电话')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    occupant_count = db.Column(db.Integer, nullable=False, default=0, comment='入住人数')
    check_in_date = db.Column(db.Date, nullable=True, comment='入住时间')
    rental_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='租赁状态：1=已缴费, 2=未缴费')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='更新时间')


class RentalInfoNew(db.Model):
    __tablename__ = 'rental_info_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    room_number = db.Column(db.String(50), nullable=False, comment='房号')
    tenant_name = db.Column(db.String(50), nullable=False, comment='租客姓名')
    phone = db.Column(db.String(20), nullable=False, comment='电话')
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='押金')
    occupant_count = db.Column(db.Integer, nullable=False, default=0, comment='入住人数')
    check_in_date = db.Column(db.Date, nullable=True, comment='入住时间')
    rental_status = db.Column(db.SmallInteger, nullable=False, default=1, comment='租赁状态：1=已缴费, 2=未缴费')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment='更新时间')
