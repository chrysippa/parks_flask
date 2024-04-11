from flask import Flask, render_template

#app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app = Flask(__name__)

@app.route('/')
def index():
  my_var = 'hola'
  my_list = ['pistachio', 'almond', 'cashew']
  return render_template('index.html', my_var=my_var, my_list=my_list)

@app.route('/afton') # actually make a route for each park
def park():
  info = {}
  info['name'] = 'Afton State Park'
  info['id'] = 1
  return render_template('park.html', info=info)

@app.route('/_ah/warmup')
def warmup():
  #any warmup logic here. Returns empty string, HTTP code 200, empty object.
  return '', 200, {}

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000, debug=True)