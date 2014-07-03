from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import correlation

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

    def similarity(self, other):
        u_ratings = {}
        paired_ratings = []
        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.rating, r.rating) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0

    def predict_rating(self, movie):
        other_ratings = movie.ratings
        similarities = [ (self.similarity(r.user), r) \
            for r in other_ratings ]
        similarities.sort(reverse=True)
        similarities = [ s for s in similarities if s[0] > 0 ]
        if not similarities:
            return None
        numerator = sum( [ r.rating * s for s, r in similarities ] )
        denominator = sum( [ s[0] for s in similarities ] )
     
        return numerator / denominator


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    released_at = Column(DateTime, nullable = True)
    imdb_url = Column(String, nullable = True)

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
