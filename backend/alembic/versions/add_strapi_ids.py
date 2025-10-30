"""
Add Strapi IDs to existing tables

Revision ID: add_strapi_ids
Revises:
Create Date: 2024-01-15

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_strapi_ids'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add Strapi ID columns to existing tables"""

    # Add strapi_id to projects table
    op.add_column('projects', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_projects_strapi_id', 'projects', ['strapi_id'])

    # Add strapi_id to creative_ideas table
    op.add_column('creative_ideas', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_creative_ideas_strapi_id', 'creative_ideas', ['strapi_id'])

    # Add strapi_id to scripts table
    op.add_column('scripts', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_scripts_strapi_id', 'scripts', ['strapi_id'])

    # Add strapi_id to storyboards table
    op.add_column('storyboards', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_storyboards_strapi_id', 'storyboards', ['strapi_id'])

    # Add strapi_id to media_assets table
    op.add_column('media_assets', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_media_assets_strapi_id', 'media_assets', ['strapi_id'])

    # Add strapi_id to final_videos table
    op.add_column('final_videos', sa.Column('strapi_id', sa.String(length=100), nullable=True))
    op.create_index('ix_final_videos_strapi_id', 'final_videos', ['strapi_id'])


def downgrade():
    """Remove Strapi ID columns from tables"""

    # Remove strapi_id from final_videos table
    op.drop_index('ix_final_videos_strapi_id', 'final_videos')
    op.drop_column('final_videos', 'strapi_id')

    # Remove strapi_id from media_assets table
    op.drop_index('ix_media_assets_strapi_id', 'media_assets')
    op.drop_column('media_assets', 'strapi_id')

    # Remove strapi_id from storyboards table
    op.drop_index('ix_storyboards_strapi_id', 'storyboards')
    op.drop_column('storyboards', 'strapi_id')

    # Remove strapi_id from scripts table
    op.drop_index('ix_scripts_strapi_id', 'scripts')
    op.drop_column('scripts', 'strapi_id')

    # Remove strapi_id from creative_ideas table
    op.drop_index('ix_creative_ideas_strapi_id', 'creative_ideas')
    op.drop_column('creative_ideas', 'strapi_id')

    # Remove strapi_id from projects table
    op.drop_index('ix_projects_strapi_id', 'projects')
    op.drop_column('projects', 'strapi_id')