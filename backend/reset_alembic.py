from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # 刪除 alembic_version 表
    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()
    print("已刪除 alembic_version 表")