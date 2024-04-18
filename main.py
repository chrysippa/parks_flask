from google.cloud.bigquery_storage import BigQueryReadClient, types
import datetime
from flask import Flask, render_template

#app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app = Flask(__name__)

@app.route('/')
def index():
	parks = [{'name': 'Afton State Park', 'summary': 'good'}, {'name': 'Banning State Park', 'summary': 'warn'}] #  In alphabetical order by name
	date = '4-18'
	#parks = get_all_parks()
	return render_template('index.html', parks=parks, date=date)

@app.route('/afton') # actually make a route for each park
def park():
    # call a func get_one_park that checks if have data from today. if not, call other func pull_all_parks.
    p = {}
    p['name'] = 'Afton State Park'
    p['id'] = 1
    p['site_url'] = 'https://www.dnr.state.mn.us/state_parks/park.html?id=spk00100#homepage'
    p['seasonal'] = {'Humidity': {'value': 60, 'level': 'good'}, 'Pollen mold': {'value': 'low', 'level': 'good'}}
    # pass tomorrow conditions as t = {...} ? and incl the seasonal fields in it bc they'll go in same table as weather
    t = {}
    t['seasonal'] = {'Pollen mold': {'value': 'low', 'level': 'good'}}
    #park_id = 1
    #p = get_one_park(park_id)
    return render_template('park.html', p=p, t=t)

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