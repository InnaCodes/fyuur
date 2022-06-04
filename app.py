#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
       return f"<Venue id={self.id} name={self.name} city={self.city} state={self.state}>"

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref="artists", lazy=True)

    def __repr__(self):
       return f"<Artist id={self.id} name={self.name} city={self.city} state={self.state}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id}>"
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  Latest_venues = Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()
  Latest_artists = Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
  return render_template('pages/home.html', venues=Latest_venues, artists=Latest_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  get_result = Venue.query.distinct(Venue.city, Venue.state).all()
  for item in get_result:
    location = {
      "city": item.city,
      "state": item.state
    }

    venues = Venue.query.filter_by(city=item.city, state=item.state).all()

    changed_venues=[]

    for result in venues:
      
      changed_venues.append({
        "id": result.id,
        "name": result.name,
        "num_upcoming_shows": result.num_upcoming_shows
      })

    location['venues'] = changed_venues
    data.append(location)

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", "")
  response={}

  venues = list(Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%") |
    Venue.state.ilike(f"%{search_term}%") |
    Venue.city.ilike(f"%{search_term}%")
  ).all())

  response['count'] = len(venues)
  response['data'] = []

  for venue in venues:
    block = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.num_upcoming_shows
    }

    response['data'].append(block)

  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  today_date = datetime.now()
  shows = venue.show

  for show in shows:
    info = { 
      "artist_id" : show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    if (show.start_time > today_date):
      upcoming_shows.append(info)
    else:
      past_shows.append(info)

  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  check= False
  if request.form['seeking_talent'] == "y":
    check = True
  
  new_venue = Venue()
  new_venue.name = request.form['name']
  new_venue.city = request.form['city']
  new_venue.state = request.form['state']
  new_venue.address = request.form['address']
  new_venue.phone = request.form['phone']
  new_venue.genres = request.form['genres']
  new_venue.image_link = request.form['image_link']
  new_venue.facebook_link = request.form['facebook_link']
  new_venue.website_link = request.form['website_link']
  new_venue.seeking_talent = check
  new_venue.seeking_description = request.form['seeking_description']

  try:
    db.session.add(new_venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue_id = request.form.get('venue_id')
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue could not be deleted!')
  finally:
    db.session.close()
  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.distinct(Artist.id, Artist.name).all()
  for artist in artists:
    info={
      "id": artist.id,
      "name": artist.name
    }
    data.append(info)

  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term", "")
  response = {}

  artists = list(Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%")).all())

  response["count"] = len(artists)
  response["data"] = []

  for artist in artists:
    info = {
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": artist.num_upcoming_shows
    }
    response["data"].append(info) 
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = artist.show
  past_shows=[]
  upcoming_shows = []
  today_date = datetime.now()
  for show in shows:
    info={
      "venue_id": show.id,
      "venue_name": show.venues.name,
      "venue_image_link": show.venues.image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    if (show.start_time > today_date):
      upcoming_shows.append(info)
    else:
      past_shows.append(info)

  data ={
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres.split(','),
    "facebook_link": artist.facebook_link,
    "website_link": artist.website_link,
    "image_link": artist.image_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_id = Artist.query.get(artist_id)
  artist = {
    "id": artist_id.id,
    "name": artist_id.name,
    "city": artist_id.city,
    "state": artist_id.state,
    "phone": artist_id.phone,
    "genres": artist_id.genres,
    "facebook_link": artist_id.facebook_link,
    "website_link": artist_id.website_link,
    "image_link": artist_id.image_link,
    "seeking_venue": artist_id.seeking_venue,
    "seeking_description": artist_id.seeking_description
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  check= False
  if request.form['seeking_venue'] == "y":
    check = True
  
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form['genres']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.image_link = request.form['image_link']
  artist.seeking_venue = check
  artist.seeking_description = request.form['seeking_description']

  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' has been successfully edited')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not be edited')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_id = Venue.query.get(venue_id)
  venue = {
    "id": venue_id.id,
    "name": venue_id.name,
    "city": venue_id.city,
    "state": venue_id.state,
    "phone": venue_id.phone,
    "address": venue_id.address,
    "genres": venue_id.genres,
    "facebook_link": venue_id.facebook_link,
    "website_link": venue_id.website_link,
    "image_link": venue_id.image_link,
    "seeking_talent": venue_id.seeking_talent,
    "seeking_description": venue_id.seeking_description
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  check= False
  if request.form['seeking_talent'] == "y":
    check = True
  
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form['genres']
  venue.facebook_link = request.form['facebook_link']
  venue.website_link = request.form['website_link']
  venue.image_link = request.form['image_link']
  venue.seeking_talent = check
  venue.seeking_description = request.form['seeking_description']
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' has been successfully edited')
  except:
    print(sys.exc_info())
    db.session.rollback
    flash('Error Artist ' + request.form['name'] + ' could not be edited')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  check= False
  if request.form['seeking_talent'] == "y":
    check = True
  new_artist = Artist()
  new_artist.name = request.form['name']
  new_artist.city = request.form['city']
  new_artist.state = request.form['state']
  new_artist.phone = request.form['phone']
  new_artist.genres = request.form['genres']
  new_artist.image_link = request.form['image_link']
  new_artist.facebook_link = request.form['facebook_link']
  new_artist.website_link = request.form['website_link']
  new_artist.seeking_venue = check
  new_artist.seeking_description = request.form['seeking_description']
  try:
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows = Show.query.all()
  for show in shows:
    info={
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": str(show.start_time)
    }
    data.append(info)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    new_shows = Show()
    new_shows.artist_id = request.form['artist_id']
    new_shows.venue_id = request.form['venue_id']
    new_shows.start_time = str(request.form['start_time'])

    db.session.add(new_shows)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
