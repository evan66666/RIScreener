from sqlalchemy import event
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# SQLite connect args for thread safety and high concurrency in FastAPI
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False, "timeout": 30.0},
    echo=False
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def _migrate_columns():
    """Automatically ensures all SQLModel declared columns exist in existing SQLite tables."""
    from sqlalchemy import inspect
    insp = inspect(engine)
    with engine.connect() as conn:
        # Migrate evidence table if document_signal_id has NOT NULL constraint
        if insp.has_table("evidence"):
            for col in insp.get_columns("evidence"):
                if col["name"] == "document_signal_id" and not col["nullable"]:
                    try:
                        print("[DB Migration] Migrating evidence table to allow NULL on document_signal_id...")
                        conn.exec_driver_sql("ALTER TABLE evidence RENAME TO evidence_old")
                        SQLModel.metadata.tables["evidence"].create(conn)
                        conn.exec_driver_sql(
                            "INSERT INTO evidence (id, document_signal_id, source_document_id, page_number, excerpt, evidence_type, extraction_confidence) "
                            "SELECT id, document_signal_id, source_document_id, page_number, excerpt, evidence_type, extraction_confidence FROM evidence_old"
                        )
                        conn.exec_driver_sql("DROP TABLE evidence_old")
                        conn.commit()
                        print("[DB Migration] evidence table migration complete.")
                    except Exception as e:
                        print(f"[DB Migration Error] evidence table: {e}")
                    break

        for table_name, table in SQLModel.metadata.tables.items():
            if insp.has_table(table_name):
                existing = {col["name"] for col in insp.get_columns(table_name)}
                for col in table.columns:
                    if col.name not in existing:
                        col_type = col.type.compile(engine.dialect)
                        default_clause = ""
                        if col.default is not None and hasattr(col.default, 'arg'):
                            if isinstance(col.default.arg, (int, float)):
                                default_clause = f" DEFAULT {col.default.arg}"
                            elif isinstance(col.default.arg, str):
                                default_clause = f" DEFAULT '{col.default.arg}'"
                            elif isinstance(col.default.arg, bool):
                                default_clause = f" DEFAULT {1 if col.default.arg else 0}"
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}{default_clause}"
                        try:
                            conn.exec_driver_sql(alter_sql)
                            conn.commit()
                            print(f"[DB Migration] Added column {table_name}.{col.name} ({col_type})")
                        except Exception as e:
                            print(f"[DB Migration Error] {table_name}.{col.name}: {e}")


def init_db():
    from app.models.schema import (
        Company, Actor, ActorAlias, ActorRelationship,
        Announcement, Document, DocumentPage,
        OwnershipSnapshot, OwnershipEvent, TransactionEvent,
        CorporateActionEvent, DocumentSignal, Evidence,
        ActorBehaviorState, IssuerIntelligenceState,
        IssuerActionState, SignalEvent, Scan, RuleVersion,
        InvestorClassification, MarketStructureSnapshot,
        CorporateActionAssessment
    )
    SQLModel.metadata.create_all(engine)
    _migrate_columns()

def get_session():
    with Session(engine) as session:
        yield session
