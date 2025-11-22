from sqlmodel import SQLModel, Session, create_engine, select
from app.models import User
from app.auth import get_password_hash

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    """初始化数据库，创建默认用户"""
    create_db_and_tables()
    
    with Session(engine) as session:
        # 检查并创建/更新 admin 用户
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            # 创建新用户
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                user_type="admin",
            )
            admin_user.roles = ["admin"]
            admin_user.permissions = ["view_pc", "view_fs", "manage_users"]
            session.add(admin_user)
        else:
            # 更新已存在用户的角色和权限（如果为空或需要更新）
            if not admin_user.roles_json or admin_user.roles_json == "[]":
                admin_user.roles = ["admin"]
            if not admin_user.permissions_json or admin_user.permissions_json == "[]":
                admin_user.permissions = ["view_pc", "view_fs", "manage_users"]
            session.add(admin_user)
        
        # 检查并创建/更新 user 用户
        normal_user = session.exec(select(User).where(User.username == "user")).first()
        if not normal_user:
            normal_user = User(
                username="user",
                hashed_password=get_password_hash("user123"),
                user_type="internal",
            )
            normal_user.roles = ["user"]
            normal_user.permissions = ["view_pc"]
            session.add(normal_user)
        else:
            # 更新已存在用户的角色和权限（如果为空或需要更新）
            if not normal_user.roles_json or normal_user.roles_json == "[]":
                normal_user.roles = ["user"]
            if not normal_user.permissions_json or normal_user.permissions_json == "[]":
                normal_user.permissions = ["view_pc"]
            session.add(normal_user)
        
        session.commit()
