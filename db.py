import pandas as pd
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

Base = declarative_base()

DBNAME = "hippo_map_tool"


class Table(Base):
    __tablename__ = 'table'

    uid = Column(String(20), primary_key=True)
    name = Column(String(20), nullable=False)


engine = create_engine(
    f"sqlite:///{DBNAME}.db?check_same_thread=False", echo=True)
Base.metadata.create_all(engine, checkfirst=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def init_db(engine, session, batch_size=10000):
    if not engine.execute("select count(1) from table").first()[0]:
        df = pd.read_csv("table.tsv", sep="\t", names=["uid", "name"])
        for ix, row in tqdm(df.iterrows()):
            session.add(Table(uid=row.uid, name=row.name))
            if ix % batch_size == 0:
                session.commit()
        session.commit()


def get_name_by_uid(uid):
    q = session.query(Table).filter(Table.uid == uid).one_or_none()
    return q.name if q else None


if __name__ == "__main__":
    init_db(engine, session)
