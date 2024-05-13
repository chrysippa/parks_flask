from google.cloud.bigquery_storage import BigQueryReadClient, types
import datetime
from flask import Flask, render_template, abort, request

# Local data cache
index_data = []
single_park_data = {}
js_data = []
date_updated = ''

app = Flask(__name__)

@app.route('/')
def index():
    """Return homepage"""
    # Update data cache if empty
    if not index_data:
        pull_from_db()

    parks = index_data
    date = date_updated
    return render_template('index.html', parks=parks, date=date)

@app.route('/parks/<park_id>')
def park(park_id):
    """Return individual park page"""
    # Update data cache if empty
    if not single_park_data:
        pull_from_db()

    # 404 if nonexistent park
    id = int(park_id)
    if id not in single_park_data.keys():
        abort(404)
    else:
        park = single_park_data[id]
        p = park['park_basics']
        tod = park['today']
        tom = park['tomorrow']
        return render_template('park.html', p=p, tod=tod, tom=tom)
    
@app.route('/index_script')
def render_js():
    """Return homepage JavaScript (dynamically generated)"""
    parks = js_data
    return render_template('index_script.js', parks=parks)

@app.route('/tasks/pull-data')
def pull_data():
    """Cron job to update data cache every morning"""
    # Ensure request comes from App Engine
    try:
        if request.headers['X-Appengine-Cron']:
            pull_from_db()
            return '', 200
    except KeyError:
        pass

@app.route('/_ah/warmup')
def warmup():
    """Warmup function required in order to have minimum number of instances"""
    pull_from_db()
    return '', 200, {}

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('not_found.html'), 404


def pull_table(client, table_name, where):
    """Pull data from a single BigQuery table
    Returns data as list of dictionaries"""
    table = f'projects/parks-414615/datasets/parks/tables/{table_name}'

    requested_session = types.ReadSession()
    requested_session.table = table
    requested_session.data_format = types.DataFormat.AVRO
    requested_session.read_options.row_restriction = where # WHERE clause
    parent = 'projects/parks-414615'
    session = client.create_read_session(
        parent=parent,
        read_session=requested_session,
        max_stream_count=1
    )
    reader = client.read_rows(session.streams[0].name)
    rows = reader.rows(session)

    data = []
    try:
        for row in rows:
            data.append(row)
    except EOFError:
        pass
    return data

def format_single_park_data(tod, tom, basics, w_alerts, days):
    """Format data to store in single_park_data cache
    Arguments: raw lists of dictionaries, pulled from database
    Returns dictionary with park entries in this format:
    123: {'park_basics': {}, 'today': {}, 'tomorrow': {} }"""
    # Establish dates for season cutoffs
    current_date = datetime.date.today()
    tomorrow_date = current_date + datetime.timedelta(days=1)
    year_start = current_date.replace(month=1, day=1)
    winter_end = current_date.replace(month=4, day=15)
    spring_start = current_date.replace(month=3, day=1)
    spring_end = current_date.replace(month=5, day=31)
    summer_start = current_date.replace(month=5, day=10)
    summer_end = current_date.replace(month=7, day=15)
    fall_start = current_date.replace(month=7, day=1)
    fall_end = current_date.replace(month=11, day=15)
    winter_start = current_date.replace(month=11, day=1)
    year_end = current_date.replace(month=12, day=31)

    formatted = {}
    
    for park in basics:
        p_id = park['park_id']

        # Format its basic information
        # ----------------------------
        basics_cols_to_keep = ['name', 'city', 'site_url', 'maps_url']
        park_basics = {k:v for k, v in park.items() if k in basics_cols_to_keep}

        # Format its conditions today
        # ---------------------------
        today = {}

        tod_cols_unaltered = ['weather_icon', 'weather_description', 'precip_type', 'air_quality_type', 'holiday', 'special_park_day', 'sunrise', 'sunset']
        tod_cols_add_level = ['temp_max_f', 'feels_like_max_f', 'precip_prob', 'precip_depth_in', 'cloud_cover_percent', 'max_wind_mph', 'air_quality_level']

        tod_raw = {}
        for tod_park in tod:
            if tod_park['park_id'] == p_id: # find matching row in raw data
                tod_raw = tod_park

        for col, data in tod_raw.items():
            if col in tod_cols_unaltered:
                today[col] = data
            if col in tod_cols_add_level:
                today[col] = {'val': data, 'level': ''}
            if col == 'precip_yesterday_in':
                tod_yester_precip = data
            if col == 'precip_2_days_ago_in':
                tod_2_ago_precip = data

        today['precip_last_2_days'] = {'val': round(tod_yester_precip + tod_2_ago_precip, 2), 'level': ''}
        
        # Add seasonal factors according to the current season
        today['seasonal'] = {}
        if (current_date >= year_start and current_date <= winter_end) or (current_date >= winter_start and current_date <= year_end):
            today['seasonal']['Snow depth (inches)'] = {'val': tod_raw['snowpack_depth_in'], 'level': ''}
        if current_date >= spring_start and current_date <= spring_end:
            today['seasonal']['Pollen (tree)'] = {'val': tod_raw['pollen_tree'], 'level': ''}
        if current_date >= summer_start and current_date <= summer_end:
            today['seasonal']['Pollen (grass)'] = {'val': tod_raw['pollen_grass'], 'level': ''}
            today['seasonal']['Pollen (ragweed)'] = {'val': tod_raw['pollen_ragweed'], 'level': ''}
            today['seasonal']['Mold spores'] = {'val': tod_raw['pollen_mold'], 'level': ''}
            today['seasonal']['UV index'] = {'val': tod_raw['uv_index'], 'level': ''}
            today['seasonal']['Humidity (%)'] = {'val': tod_raw['humidity'], 'level': ''}
        if current_date >= fall_start and current_date <= fall_end:
            today['seasonal']['Pollen (ragweed)'] = {'val': tod_raw['pollen_ragweed'], 'level': ''}
            today['seasonal']['Mold spores'] = {'val': tod_raw['pollen_mold'], 'level': ''}

        today['special_day_notes'] = []
        if days:
            for row in days:
                if row['date'] == current_date.isoformat():
                    today['special_day_notes'].append(row['note'])

        today['weather_alerts'] = []
        if w_alerts:
            for row in w_alerts:
                this_park_alerts = [row['alert'] for row in w_alerts if row['park_id'] == p_id]
                today['weather_alerts'] = this_park_alerts

        today['weather_header'] = ''
        today['alerts_header'] = ''
        today['seasonal_header'] = ''
        today['header'] = ''

        # Format its conditions tomorrow
        # ------------------------------
        tomorrow = {}

        tom_cols_unaltered = tod_cols_unaltered
        rm_from_tod_cols = ['sunrise', 'sunset']
        for col in rm_from_tod_cols:
            tom_cols_unaltered.remove(col)
        tom_cols_add_level = tod_cols_add_level

        tom_raw = {}
        for tom_park in tom:
            if tom_park['park_id'] == p_id: # find matching row in raw data
                tom_raw = tom_park

        for col, data in tom_raw.items():
            if col in tom_cols_unaltered:
                tomorrow[col] = data
            if col in tom_cols_add_level:
                tomorrow[col] = {'val': data, 'level': ''}
            if col == 'precip_yesterday_in':
                tom_yester_precip = data
            if col == 'precip_2_days_ago_in':
                tom_2_ago_precip = data

        tomorrow['precip_last_2_days'] = {'val': round(tom_yester_precip + tom_2_ago_precip, 2), 'level': ''}
        
        # Add seasonal factors according to the current season
        tomorrow['seasonal'] = {}
        if (tomorrow_date >= year_start and tomorrow_date <= winter_end) or (tomorrow_date >= winter_start and tomorrow_date <= year_end):
            tomorrow['seasonal']['Snow depth (inches)'] = {'val': tom_raw['snowpack_depth_in'], 'level': ''}
        if tomorrow_date >= spring_start and tomorrow_date <= spring_end:
            tomorrow['seasonal']['Pollen (tree)'] = {'val': tom_raw['pollen_tree'], 'level': ''}
        if tomorrow_date >= summer_start and tomorrow_date <= summer_end:
            tomorrow['seasonal']['Pollen (grass)'] = {'val': tom_raw['pollen_grass'], 'level': ''}
            tomorrow['seasonal']['Pollen (ragweed)'] = {'val': tom_raw['pollen_ragweed'], 'level': ''}
            tomorrow['seasonal']['Mold spores'] = {'val': tom_raw['pollen_mold'], 'level': ''}
            tomorrow['seasonal']['UV index'] = {'val': tom_raw['uv_index'], 'level': ''}
            tomorrow['seasonal']['Humidity (%)'] = {'val': tom_raw['humidity'], 'level': ''}
        if tomorrow_date >= fall_start and tomorrow_date <= fall_end:
            tomorrow['seasonal']['Pollen (ragweed)'] = {'val': tom_raw['pollen_ragweed'], 'level': ''}
            tomorrow['seasonal']['Mold spores'] = {'val': tom_raw['pollen_mold'], 'level': ''}

        tomorrow['special_day_notes'] = []
        if days:
            for row in days:
                if row['date'] == tomorrow_date.isoformat():
                    tomorrow['special_day_notes'].append(row['note'])

        tomorrow['weather_header'] = ''
        tomorrow['alerts_header'] = ''
        tomorrow['seasonal_header'] = ''
        tomorrow['header'] = ''

        # Insert with park_id as its key
        # ------------------------------
        formatted[p_id] = {'park_basics': park_basics, 'today': today, 'tomorrow': tomorrow}

    return formatted

def assign_levels(data):
    """Assign factors to levels: one of 'good', 'warning', or 'bad'
    Arguments: formatted single_park_data dictionary
    Returns single_park_data dictionary"""
    # Define cutoffs for each factor
    numeric_cutoffs_high = {
        'temp_max_f': {'warning': 85, 'bad': 90},
        'feels_like_max_f': {'warning': 87, 'bad': 95},
        'precip_prob': {'warning': 50, 'bad': 90},
        'precip_depth_in': {'warning': 0.5, 'bad': 1.0},
        'cloud_cover_percent': {'warning': 90, 'bad': 110}, # Avoid triggering 'bad' for cloud cover
        'max_wind_mph': {'warning': 25, 'bad': 35},
        'precip_last_2_days': {'warning': 0.5, 'bad': 1.0}
    }
    numeric_cutoffs_low = {
        'temp_max_f': {'warning': 50, 'bad': 20},
        'feels_like_max_f': {'warning': 50, 'bad': 25}
    }
    text_cutoffs = {
        'air_quality_level': {'warning': ['moderate'], 'bad': ['high', 'unhealthy', 'hazardous'] }
    }
    seasonal_numeric = {
        'Snow depth (inches)': {'warning': 1.5, 'bad': 3.0},
        'UV index': {'warning': 6, 'bad': 9},
        'Humidity (%)': {'warning': 70, 'bad': 90}
    }
    seasonal_text = {
        'Pollen (tree)': {'warning': ['Moderate'], 'bad': ['High']},
        'Pollen (grass)': {'warning': ['Moderate'], 'bad': ['High']},
        'Pollen (ragweed)': {'warning': ['Moderate'], 'bad': ['High']},
        'Mold spores': {'warning': ['Moderate'], 'bad': ['High']},
    }
    
    # Score each park
    for park in data.values():
        for d in ['today', 'tomorrow']:
            day = park[d]

            weather_header_values = []

            # Score number-based factors
            for datum, levels in numeric_cutoffs_high.items():
                to_score = day[datum]['val']
                bad = levels['bad']
                warning = levels['warning']
                if to_score >= bad:
                    day[datum]['level'] = 'bad'
                    weather_header_values.append('bad')
                elif to_score >= warning:
                    day[datum]['level'] = 'warning'
                    weather_header_values.append('warning')
                else:
                    day[datum]['level'] = 'good'
                
            for datum, levels in numeric_cutoffs_low.items():
                to_score = day[datum]['val']
                bad = levels['bad']
                warning = levels['warning']
                if to_score <= bad:
                    day[datum]['level'] = 'bad'
                    weather_header_values.append('bad')
                elif to_score <= warning:
                    day[datum]['level'] = 'warning'
                    weather_header_values.append('warning')

            # Score text-based factors
            for datum, levels in text_cutoffs.items():
                to_score = day[datum]['val']
                bad = levels['bad']
                warning = levels['warning']
                if to_score in bad:
                    day[datum]['level'] = 'bad'
                    weather_header_values.append('bad')
                elif to_score in warning:
                    day[datum]['level'] = 'warning'
                    weather_header_values.append('warning')
                else:
                    day[datum]['level'] = 'good'

            # Score any seasonal factors
            seasonal_header_value = 'good'
            for name, details in day['seasonal'].items():
                to_score = details['val']
                if name in seasonal_numeric.keys():
                    bad = seasonal_numeric[name]['bad']
                    warning = seasonal_numeric[name]['warning']
                    if to_score >= bad:
                        day['seasonal'][name]['level'] = 'bad'
                        # Seasonal values should only affect higher-level summaries if the numeric data are severe
                        # And should only cause a 'warning'
                        seasonal_header_value = 'warning' 
                    elif to_score >= warning:
                        day['seasonal'][name]['level'] = 'warning'
                    else:
                        day['seasonal'][name]['level'] = 'good'
                else:
                    bad = seasonal_text[name]['bad']
                    warning = seasonal_text[name]['warning']
                    if to_score in bad:
                        day['seasonal'][name]['level'] = 'bad'
                    elif to_score in warning:
                        day['seasonal'][name]['level'] = 'warning'
                    else:
                        day['seasonal'][name]['level'] = 'good'

            # Set weather subheader
            if 'bad' in weather_header_values:
                day['weather_header'] = 'bad'
            elif 'warning' in weather_header_values:
                day['weather_header'] = 'warning'
            else:
                day['weather_header'] = 'good'
            # Weather alerts trigger a 'warning' unless already 'bad'
            if d == 'today' and day['weather_alerts']:
                if day['weather_header'] != 'bad':
                    day['weather_header'] = 'warning'

            # Set park alerts subheader
            day['alerts_header'] = 'warning' if day['special_day_notes'] else 'good'

            # Set seasonal subheader
            day['seasonal_header'] = seasonal_header_value

            # Set main header
            subheader_values = [day['weather_header'], day['alerts_header'], day['seasonal_header']]
            if 'bad' in subheader_values:
                day['header'] = 'bad'
            elif 'warning' in subheader_values:
                day['header'] = 'warning'
            else:
                day['header'] = 'good'
        
    return data

def format_index_data(data):
    """Formats data to store in index_data cache
    Arguments: raw list of dictionaries, pulled from database
    Returns list of dictionaries in this format:
    {'park_id': 123, 'name': 'Afton State Park', 'level': 'warning'}"""
    formatted = []
    for park in data:
        formatted.append({'park_id': park['park_id'], 'name': park['name']})
    formatted.sort(key=lambda d: d['name']) # sort alphabetically by park name
    for park in formatted:
        id = park['park_id']
        park['level'] = single_park_data[id]['today']['header']
    return formatted

def format_js_data(basics, single_parks):
    """Formats data to store in js_data cache
    Arguments: raw list of dictionaries, pulled from database
    Returns list of dictionaries in this format:
    {'park_id': 123, 'name': 'Afton State Park', 'latitude': 44.84681, 'longitude': -92.79139, 'level': 'warning'}"""
    cols_to_keep = ['park_id', 'name', 'latitude', 'longitude']
    formatted = []
    for park in basics:
        keep = {k:v for k, v in park.items() if k in cols_to_keep}
        keep['name'] = escape_chars(keep['name'])
        p_id = keep['park_id']
        keep['level'] = single_parks[p_id]['today']['header']
        formatted.append(keep)
    return formatted

def escape_chars(s):
    """Formats strings for JavaScript escaping purposes
    Returns modified string"""
    if "'" in s:
        s = s.replace("'", "\\'")
    if "." in s:
        s = s.replace(".", "\\.")
    return s

def pull_from_db():
    """Pull data from all BigQuery tables and stores in global cache variables
    Returns None"""
    # Determine date of data to pull
    today_dt = datetime.date.today()
    today = str(today_dt)
    tomorrow = str(today_dt + datetime.timedelta(days=1))
    now = datetime.datetime.now() # Will be America/Chicago timezone due to startup script
    if now.hour == 0 or (now.hour == 1 and now.minute < 55): # ETL not finished; use yesterday's dates
        tomorrow = today
        today_dt = today_dt - datetime.timedelta(days=1)
        today = str(today_dt)
    data_date = today_dt.strftime('%A %m-%d')

    # Pull tables from BigQuery
    client = BigQueryReadClient()

    where = f'date = "{today}"' # WHERE clause
    today_conditions = pull_table(client, 'daily_conditions', where)
    
    where = f'date ="{tomorrow}"'
    tomorrow_conditions = pull_table(client, 'daily_conditions_tomorrow', where)
    
    where = None # no WHERE clause; get all columns
    parks_basics = pull_table(client, 'parks', where)

    where = f'date = "{today}"'
    weather_alerts = pull_table(client, 'weather_alerts', where)

    where = f'date = "{today}" OR date ="{tomorrow}"'
    special_days = pull_table(client, 'special_days', where)

    # Store data locally
    data_to_score = format_single_park_data(today_conditions,
                                               tomorrow_conditions,
                                               parks_basics,
                                               weather_alerts,
                                               special_days)
    global single_park_data
    single_park_data = assign_levels(data_to_score)

    global index_data
    index_data = format_index_data(parks_basics)

    global js_data
    js_data = format_js_data(parks_basics, single_park_data)

    global date_updated
    date_updated = data_date


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)