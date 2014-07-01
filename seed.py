import model
import csv
from time import strptime
from datetime import datetime

def load_users(session):
    # use u.user
    filename = '/home/user/ratings/seed_data/u.user'
    with open(filename) as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            id = int(row[0])
            age = int(row[1])
            gender = row[2].decode('latin-1')
            zipcode = row[4].decode('latin-1')
            user = model.User(id=id, age=age, gender=gender, zipcode=zipcode)
            session.add(user)

def load_movies(session):
    # use u.item
    filename = '/home/user/ratings/seed_data/u.item'
    with open(filename) as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            id = int(row[0])
            name = row[1].decode('latin-1')[0:-6]

            date = row[2]
            if not date:
                released_at = None
            else:
                released_at = datetime.strptime(date, "%d-%b-%Y")

            imdb_url = row[4].decode('latin-1')

            movie = model.Movie(id=id, name=name, released_at=released_at, imdb_url=imdb_url)
            session.add(movie)

def load_ratings(session):
    # use u.data
    filename = '/home/user/ratings/seed_data/u.data'
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            content = row[0]
            row_data = content.split()
        
            user_id = int(row_data[0])
            movie_id = int(row_data[1])
            rating = int(row_data[2])

            rating = model.Rating(user_id=user_id, movie_id=movie_id, rating=rating)
            session.add(rating)

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    load_movies(session)
    load_ratings(session)
    session.commit()

if __name__ == "__main__":
    s= model.connect() #this is obsolete as of part 2 Ch 2
    main(s)
