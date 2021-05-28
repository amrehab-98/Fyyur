#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# import models for external files
from models import db, Venue, Artist, Show

# db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database





def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  data = []
  # filter venues by areas and show them
  for place in places:
    places = Venue.query.filter_by(
        state=place.state).filter_by(city=place.city).all()
    venue_data = []
    for venue in places:
      venue_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
      })
      data.append({
        'city': place.city,
        'state': place.state,
        'venues': venue_data
      })
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  
  #query for venues containing the search term case insensetive
  search = Venue.query.filter(Venue.name.ilike(
      f"%{request.form.get('search_term', '')}%"))
  data = []
  for item in search:
      data.append({"id": item.id,
                   "name": item.name,
                   "num_upcoming_shows": Show.query.filter(Show.venue_id == item.id).filter(Show.start_time > datetime.now()).count()
                   })
  response = {
    "count": search.count(),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    # shows = Show.query.filter(Show.venue_id == venue_id).all()
    # JOIN query to find past_shows
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    # print(f"FIND ME EEEE {past_shows_query}")
    # JOIN query to find upcoming_shows
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time >= datetime.now()).all()
    past_shows = []
    upcoming_shows = []
    
    #method without JOIN query :)
    # for show in shows:
    #   entry = {
    #     "artist_id": show.artist_id,
    #     "artist_name": show.artist.name,
    #     "artist_image_link": show.artist.image_link,
    #     "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    #   }
    #   if(show.start_time >= datetime.now()):
    #     upcoming_shows.append(entry)
    #   else:
    #     past_shows.append(entry)
        
    # turn start time into string in order for it to parse 
    for show in past_shows_query:
      entry = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
      past_shows.append(entry)
    for show in upcoming_shows_query:
      entry = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
      upcoming_shows.append(entry)
      
    #data dict contains all needed data for a given venue  
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(","),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    
    return render_template('pages/show_venue.html', venue = data)


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
  try:
    # create new venue with data from create venue form
    venue = Venue()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.facebook_link = request.form.get('facebook_link')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    # try to add it to database
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    #if fails rollback session
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    #close database connection
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
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
  data = Artist.query.order_by(Artist.id).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  #query for artists name containing search term, case insensitive
  search = Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%"))
  data = []
  for item in search:
      data.append({"id": item.id,
                   "name": item.name,
                   "num_upcoming_shows": Show.query.filter(Show.artist_id==item.id).filter(Show.start_time > datetime.now()).count()
                   })
  response = {
    "count": search.count(),
    "data": data
  }
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter(Show.artist_id == artist_id).all()
  
  #past shows JOIN query
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  #upcoming shows JOIN query
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()

  past_shows = []
  upcoming_shows = []
    
  #old method not using JOIN query  
  # for show in shows:
  #   entry = {
  #       "artist_id": show.artist_id,
  #       "artist_name": show.artist.name,
  #       "artist_image_link": show.artist.image_link,
  #       "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
  #     }
  #   if(show.start_time >= datetime.now()):
  #     upcoming_shows.append(entry)
  #   else:
  #     past_shows.append(entry)
  
  #change start time into string and populating past_shows
  for show in past_shows_query:
    entry = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    past_shows.append(entry)
      
    #populating upcoming_shows
  for show in upcoming_shows_query:
    entry = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    upcoming_shows.append(entry)


#populating data for artist to be shown
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(","),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
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
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  try:
    #query for artist and edit his date from the form
    artist= Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.address = request.form.get('address')
    artist.facebook_link = request.form.get('facebook_link')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    #add changes to database
    db.session.add(artist)
    db.session.commit()
  except:
    #if failed rollback
    db.session.rollback()
  finally:
    #close connection
    db.session.close()  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    # query for venue and edit its data from form
    venue= Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.facebook_link = request.form.get('facebook_link')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    # add changes to database
    db.session.add(venue)
    db.session.commit()
  except:
    # if fail rollback
    db.session.rollback()
  finally:
    # close connection to database
    db.session.close()    
  # venue record with ID <venue_id> using the new attributes
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
  try:
    # create new artist
    artist = Artist()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.address = request.form.get('address')
    artist.facebook_link = request.form.get('facebook_link')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    # TODO: modify data to be the data object returned from db insertion
    # add to database
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # if fail rollback
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    # close database connection
    db.session.close()    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    entry ={
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(entry)
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
    # create new show
    show = Show()
    show.artist_id = request.form.get('artist_id')
    show.venue_id = request.form.get('venue_id')
    show.start_time = request.form.get('start_time')
    # add it to database
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    #if fail rollback
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')   
  finally:
    #close database connection
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
