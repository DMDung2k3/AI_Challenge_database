from connections import db_manager
from models import create_all_tables

engine = db_manager.get_sql_engine()
create_all_tables(engine)