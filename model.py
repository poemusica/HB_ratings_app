from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

ENGINE = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=ENGINE,
                                        autocommit=False,
                                        autoflush=False))
Base = declarative_base()
Base.query = session.query_property

### Class declarations go here
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    age = Column(Integer, nullable = True)
    gender = Column(String, nullable = True)
    zipcode = Column(String(15), nullable = True)
    email = Column(String(64), nullable = True)
    password = Column(String(64), nullable = True)

    #rating = relationship("Rating")

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    released_at = Column(DateTime, nullable = True)
    imdb_url = Column(String, nullable = True)

    #rating = relationship("Rating")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key = True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey ('users.id'))
    rating = Column(Integer, nullable = False)

    user = relationship("User", 
        backref=backref("ratings", order_by=id))

    movie = relationship("Movie", 
        backref=backref("ratings", order_by=id))

### End class declarations

def main():
    global Base
    Base.metadata.create_all(ENGINE)


if __name__ == "__main__":
    main()
