from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

# SQLALCHEMY_DATABASE_URL = "postgresql://hnlwdnokggrlgm:86244c3dcf615ecb49b4adfc61ea5c51e07f1b11e9ff831c7fba6d9dff852b82@ec2-34-194-130-103.compute-1.amazonaws.com:5432/d204k3r3jcgi36"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
