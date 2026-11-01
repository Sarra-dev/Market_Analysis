from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP
from api.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id               = Column(Integer, primary_key=True, index=True)
    titre            = Column(Text)
    entreprise       = Column(Text)
    localisation     = Column(Text)
    date_publication = Column(Text)
    experience       = Column(Text)
    contrat          = Column(Text)
    description      = Column(Text)
    competences      = Column(Text)
    source           = Column(Text)
    scraped_at       = Column(TIMESTAMP)