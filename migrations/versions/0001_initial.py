from pathlib import Path
from alembic import op


revision = "0001_initial"
down_revision = None

def upgrade() -> None:
    schema_path = Path(__file__).with_suffix(".sql")
    op.execute(schema_path.read_text(encoding="utf-8"))


def downgrade() -> None:
    for table_name in (
        "issues",
        "payments",
        "orders",
        "sync_runs"
    ):
        op.drop_table(table_name)
