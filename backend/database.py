from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = "postgresql://nevil:123456@localhost:5432/weekly_devlogs"
engine = create_engine(database_url)
sessionLocal = sessionmaker(autoflush=False,bind=engine)