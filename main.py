from google.cloud.bigquery_storage import BigQueryReadClient, types
import datetime
from flask import Flask, render_template

#app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app = Flask(__name__)

@app.route('/')
def index():
	parks = [{'name': 'Afton State Park', 'park_id': 1, 'level': 'warning'}, 
          {'name': 'Banning State Park', 'park_id': 2, 'level': 'good'},
          {'name': 'Frontenac State Park', 'park_id': 3, 'level': 'good'},
          {'name': 'Gooseberry Falls State Park', 'park_id': 4, 'level': 'good'},
          {'name': 'Grand Portage State Park', 'park_id': 5, 'level': 'good'},
          {'name': 'Great River Bluffs State Park', 'park_id': 6, 'level': 'good'},
          {'name': 'Interstate State Park', 'park_id': 7, 'level': 'good'},
          {'name': 'Jay Cooke State Park', 'park_id': 8, 'level': 'good'},
          {'name': 'Lake Maria State Park', 'park_id': 9, 'level': 'good'},
          {'name': 'Lebanon Hills Regional Park', 'park_id': 17, 'level': 'good'},
          {'name': 'Mille Lacs Kathio State Park', 'park_id': 10, 'level': 'good'},
          {'name': 'Myre-Big Island State Park', 'park_id': 11, 'level': 'good'},
          {'name': 'Nerstrand Big Woods State Park', 'park_id': 12, 'level': 'good'},
          {'name': 'Spring Lake Park Reserve', 'park_id': 18, 'level': 'warning'},
          {'name': 'St. Croix State Park', 'park_id': 13, 'level': 'good'},
          {'name': 'Tettegouche State Park', 'park_id': 14, 'level': 'good'},
          {'name': 'Vermillion Falls Park', 'park_id': 19, 'level': 'warning'},
          {'name': 'Whitewater State Park', 'park_id': 15, 'level': 'good'},
          {'name': "William O'Brien State Park", 'park_id': 16, 'level': 'good'}] #  In alphabetical order by name
	date = '4-22'
	#parks = get_all_parks()
	return render_template('index.html', parks=parks, date=date)

@app.route('/parks/<park_id>')
def park(park_id):
    # if park_id in today's data, return template, else return 404

    # call a func get_one_park that checks if have data from today. if not, call other func pull_all_parks.
    p = {}
    p['name'] = 'Afton State Park'
    p['id'] = park_id
    p['city'] = 'Hastings, MN'
    p['site_url'] = 'https://www.dnr.state.mn.us/state_parks/park.html?id=spk00100#homepage'
    p['maps_url'] = 'https://maps.app.goo.gl/veKGszJpcVJt1HuF6'

    # Today conditions
    tod = {}
    tod['weather_icon'] = 'rain'
    tod['weather_description'] = 'Partly cloudy throughout the day with a chance of rain.'
    tod['temp_max_f'] = {'val': 65, 'level': 'good'}
    tod['feels_like_max_f'] = {'val': 65, 'level': 'good'}
    tod['precip_prob'] = {'val': 47, 'level': 'good'}
    tod['precip_type'] = 'Rain'
    tod['precip_depth_in'] = {'val': 0.0, 'level': 'good'}
    tod['cloud_cover_percent'] = {'val': 46, 'level': 'good'}
    tod['max_wind_mph'] = {'val': 18, 'level': 'good'}
    tod['air_quality_type'] = 'Ozone'
    tod['air_quality_level'] = {'val': 'Good', 'level': 'good'}
    tod['precip_last_2_days'] = {'val': 0.0, 'level': 'good'} # calculate from precip_yesterday_in + precip_2_days_ago_in
    tod['weather_alerts'] = []

    tod['holiday'] = True
    tod['special_park_day'] = False
    tod['special_day_notes'] = ['Earth Day']

    tod['seasonal'] = {'Pollen mold': {'val': 'Low', 'level': 'good'},
                        'Pollen tree': {'val': 'High', 'level': 'warning'},
                        'Pollen ragweed': {'val': 'Low', 'level': 'good'},
                        'Pollen grass': {'val': 'Low', 'level': 'good'}
    }

    tod['sunrise'] = '06:14'
    tod['sunset'] = '20:06'

    tod['weather_header'] = 'good'
    tod['alerts_header'] = 'warning'
    tod['seasonal_header'] = 'warning'
    tod['header'] = 'warning'

    # Tomorrow conditions 
    tom = {}
    tom['weather_icon'] = 'rain'
    tom['weather_description'] = 'Partly cloudy throughout the day with a chance of rain.'
    tom['temp_max_f'] = {'val': 58, 'level': 'good'}
    tom['feels_like_max_f'] = {'val': 58, 'level': 'good'}
    tom['precip_prob'] = {'val': 57, 'level': 'warning'}
    tom['precip_type'] = 'Rain'
    tom['precip_depth_in'] = {'val': 0.0, 'level': 'good'}
    tom['cloud_cover_percent'] = {'val': 38, 'level': 'good'}
    tom['max_wind_mph'] = {'val': 17, 'level': 'good'}
    tom['air_quality_type'] = 'Ozone'
    tom['air_quality_level'] = {'val': 'Good', 'level': 'good'}
    tom['precip_last_2_days'] = {'val': 0.0, 'level': 'good'} # calculate from precip_yesterday_in + precip_2_days_ago_in

    tom['holiday'] = False
    tom['special_park_day'] = False
    tom['special_day_notes'] = []

    tom['seasonal'] = {'Pollen mold': {'val': 'Low', 'level': 'good'},
                        'Pollen tree': {'val': 'High', 'level': 'warning'},
                        'Pollen ragweed': {'val': 'Low', 'level': 'good'},
                        'Pollen grass': {'val': 'Low', 'level': 'good'}
    }

    tom['weather_header'] = 'warning'
    tom['alerts_header'] = 'good'
    tom['seasonal_header'] = 'warning'
    tom['header'] = 'warning'

    #p = get_one_park(park_id)
    return render_template('park.html', p=p, tod=tod, tom=tom)

@app.route('/_ah/warmup')
def warmup():
	# Any warmup logic here. Returns empty string, HTTP code 200, empty object.
	# Logic should incl a call to pull_conditions and others to get the data
	return '', 200, {}


def pull_conditions():
    today_dt = datetime.date.today()
    today = str(today_dt)
    tomorrow = str(today_dt + datetime.timedelta(days=1))

    project_id = 'parks-414615'
    client = BigQueryReadClient()

    # Get daily_conditions
    table = f'projects/{project_id}/datasets/parks/tables/daily_conditions'

    requested_session = types.ReadSession()
    requested_session.table = table
    requested_session.data_format = types.DataFormat.AVRO

	#requested_session.read_options.selected_fields = [] leave this out bc want all cols?
    requested_session.read_options.row_restriction = f'date = "{today}"' # WHERE clause

    parent = f'projects/{project_id}'
    session = client.create_read_session(
	    parent=parent,
	    read_session=requested_session,
	    max_stream_count=1
	)
    reader = client.read_rows(session.streams[0].name)

    rows = reader.rows(session)

    today_conditions = []

    try:
        for row in rows:
            today_conditions.append(row) # append rows as dicts
    except EOFError:
        pass
    
    # Get daily_conditions_tomorrow
    table = f'projects/{project_id}/datasets/parks/tables/daily_conditions_tomorrow'

    requested_session = types.ReadSession()
    requested_session.table = table
    requested_session.data_format = types.DataFormat.AVRO 

    #requested_session.read_options.selected_fields = [] none bc want all cols?
    requested_session.read_options.row_restriction = f'date ="{tomorrow}"' # WHERE clause

    parent = f'projects/{project_id}'
    session = client.create_read_session(
        parent=parent,
        read_session=requested_session,
        max_stream_count=1
    )
    reader = client.read_rows(session.streams[0].name)

    rows = reader.rows(session)

    tomorrow_conditions = []

    try:
        for row in rows:
            tomorrow_conditions.append(row) # append rows as dicts
    except EOFError:
        pass
    #TODO: put the lists of dicts somewhere. Global var 

    pass

def get_all_parks():
    # to render main page
	# like get_one_park: check if exists, if so, return all. if not and is after 2am, call pull_conditions()
    pass

def get_one_park(id):
	#check if data from today&tomorrow exists and currently is after 2am
	#if so, return that park where park['park_id'] == id
	#if not, call pull_conditions()
	pass

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)