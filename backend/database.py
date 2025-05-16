from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


engine = create_engine("postgresql://ashashasadafda:1234567vocem@localhost:7777/catspy")

Base = declarative_base()


class SpyCat(Base):
    __tablename__ = "cats"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    experience = Column(Integer)
    breed = Column(String)
    salary = Column(Integer)

    missions = relationship("Mission", back_populates="cat")


class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True)
    cat_id = Column(Integer, ForeignKey("cats.id"), nullable=True)
    is_completed = Column(Boolean, default=False)

    cat = relationship("SpyCat", back_populates="missions")
    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")


class Target(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    name = Column(String)
    country = Column(String)
    notes = Column(String)
    is_completed = Column(Boolean, default=False)

    mission = relationship("Mission", back_populates="targets")
    
    
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()