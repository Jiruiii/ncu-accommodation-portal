"""manually_add_comments_table

Revision ID: 12b285e8eb3a
Revises: 20aeb749f0f7
Create Date: 2025-05-21 23:47:09.827441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12b285e8eb3a'
down_revision = '20aeb749f0f7'
branch_labels = None
depends_on = None


def upgrade():
    # 先檢查表格是否存在
    from sqlalchemy import inspect, Table, MetaData
    from alembic import op
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    # 只在表格不存在時創建
    if 'comments' not in tables:
        op.create_table('comments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('property_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('rating', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['property_id'], ['accommodations.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        print("表格 'comments' 已存在，跳過創建")
    
    # 同樣檢查 comment_likes 表格
    if 'comment_likes' not in tables:
        op.create_table('comment_likes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('comment_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('comment_id', 'user_id', name='unique_comment_like')
        )
    else:
        print("表格 'comment_likes' 已存在，跳過創建")

def downgrade():
    op.drop_table('comment_likes')
    op.drop_table('comments')
    