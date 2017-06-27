from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd
import jinja2
import csv

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROPAGATE_EXCEPTIONS'] = True
from posts import scrapeFacebookPageFeedStatus
from comments import  scrapeFacebookPageFeedComments
from analyze import run_analysis

start_date = "2017-5-10"
end_date = "2017-5-31"
fbid = "lovemattersafrica"
access_token = "EAACEdEose0cBAFtoL239d012Gby7FxoX11Iqh5ZB4ASNkl34lct9OCHV6ZBHND2oZCSum0sBZCNPJG2a3NMVkZB3qpGcZBZCo6whaONayL2FZAFAPP1QAIC1J22eLm1irZC3v2ZAspHuz3vRZBTLLSYnpS7ZCyxeAhtLejiA0SafwwmKrQSDJaZAZBg6qkX8XrNryY790ZD"

# ROUTES:

@app.route('/')
def index():
	return render_template('index.html.jinja',summary = summary)

@app.route('/facebook', methods = ['GET','POST'])
def facebook():
	global fbid
	fbid = request.form["fbid"]
	scrapeFacebookPageFeedStatus(fbid, access_token)
	return render_template('index.html.jinja',summary = summary)

@app.route('/facebook_comments', methods = ['GET','POST'])
def facebook_comments():
	fbid_comments = request.form["fbid_comments"]
	scrapeFacebookPageFeedComments(fbid, access_token)
	return render_template('index.html.jinja',summary = summary)

@app.route('/processdate', methods = ['POST'])
def processdate():
	if request.method == 'POST':
		global start_date
		start_date = request.form["start"]
		global end_date
		end_date = request.form["end"]
	return render_template('index.html.jinja',summary = summary)

	return jsonify({'error': 'Missing either start date or end date'})

@app.route('/kickoff', methods = ['GET','POST'])
def kickoff():
	run_analysis(fbid, start_date, end_date)
	summary = pd.read_csv('%s_facebook_analysis.csv' % fbid)
	return render_template('index.html.jinja', summary = summary)

@app.route('/overview/<fbid>')
def overview(fbid):
	summary = pd.read_csv('%s_facebook_analysis.csv' % fbid)
	return render_template('overview.html.jinja', summary = summary)


if __name__ == "__main__":

	summary = pd.read_csv("lovemattersafrica_facebook_analysis.csv")

	app.run(host='127.0.0.1', port=54991, debug=True)
