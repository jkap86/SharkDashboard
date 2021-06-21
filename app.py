from flask import Flask, render_template, request, redirect, url_for, jsonify, session 
from flask_session import Session
from flask_bootstrap import Bootstrap
import requests
import json
import datetime
from operator import itemgetter
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired, AnyOf


app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
Bootstrap(app)
app.config['SECRET_KEY'] = "1111"

def getLeagues(username):
	userID = getUserIDfromUsername(username)
	leagues = requests.get('https://api.sleeper.app/v1/user/' + userID + '/leagues/nfl/2021')
	leagues = leagues.json()
	return leagues

def getUserIDfromUsername(username):
	url = requests.get('https://api.sleeper.app/v1/user/' + username)
	userID = url.json()['user_id']
	return userID

def getUsernamefromUserID(userID):
	if userID != None:
		url = requests.get('https://api.sleeper.app/v1/user/' + userID)
		username = url.json()['display_name']
	else:
		username = 'orphan'
	return username

def getAvatarThumb(userID):
	url = requests.get('https://api.sleeper.app/v1/user/' + userID)
	avatarID = url.json()['avatar']
	if avatarID != None:
		return 'https://sleepercdn.com/avatars/thumbs/' + avatarID
	else:
		return 'https://sleepercdn.com/images/logos/og_logo-66ee2f04c1dc70ba8cb5ec9f780990d1.png?vsn=d'

def getRosters(league):
	rosters = requests.get('https://api.sleeper.app/v1/league/' + league['league_id'] + '/rosters')
	rosters = rosters.json()
	return rosters


@app.route('/', methods=["POST", "GET"])
def index():
	leagues = [
	'651845915048468480', 
	'651850827601907712', 
	'651862935118913536', 
	'651869387640389632', 
	'652187077798088704', 
	'652217600155160576'
	]

	leaguesp = [
	'587545694395465728',
	'587690400039346176',
	'587700255940714496',
	'587702052977680384',
	'589705847521718272',
	'589878481194622976'

	]

	leaguesDict = []
	members = []
	for league in leaguesp:
		link = requests.get('https://api.sleeper.app/v1/league/' + league)
		leaguesDict.append({
			'name': link.json()['name'],
			'id': league,
			'avatar': 'https://sleepercdn.com/avatars/thumbs/' + link.json()['avatar']
			})
		rosters = requests.get('https://api.sleeper.app/v1/league/' + league + '/rosters')
		for roster in rosters.json():
			members.append({
				'name': getUsernamefromUserID(roster['owner_id']),
				'league': link.json()['name'],
				'wins': roster['settings']['wins'],
				'losses': roster['settings']['losses'],
				'fpts': str(roster['settings']['fpts']) + "." + str(roster['settings']['fpts_decimal']),
				'fpts_against': str(roster['settings']['fpts_against']) + "." + str(roster['settings']['fpts_against_decimal'])
				})
	members = sorted(members, key=lambda x:(x['wins'], x['fpts']), reverse=True)

	return render_template('index.html', leaguesDict=leaguesDict, members=members)