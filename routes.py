from flask import Flask, request, render_template
import jinja2

from app import app
from app import hosts_db
from app import domains_db
from app import threats_db
from app import querydb

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/configure')
def configure():
	if request.method == 'GET':
		import yaml

		with open("config.yml", 'r') as stream:
			try:
				config = yaml.load(stream)
			except yaml.YAMLError as exc:
				print(exc)
		return render_template('configure.html', config=config)
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/threats', methods=['GET', 'POST'])
def threats():
	if request.method == 'GET':
		return render_template('threats.html', hosts=hosts_db)
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/response', methods=['GET', 'POST'])
def response():
	if request.method == 'GET':
		return render_template('response.html', hosts=hosts_db)
	else:
		return "<h2> Invalid Request </h2>"

#Process for sending Quarantined MAC to ISE
@app.route('/nuke_from_space/<string:mac>', methods=['POST'])
def nuke_from_space(mac):
	from config import ise_username
	from config import ise_password
	from app import nukeFromSpace
	#nukeFromSpace(ise_username, ise_password, mac
	print (mac)
	hosts_db.update({'quarantine': 'True'}, querydb.mac == mac)
	return render_template('response.html', hosts=hosts_db)

#Process for removing Quarantined MAC to ISE
@app.route('/unnuke_from_space/<string:mac>', methods=['POST'])
def unnuke_from_space(mac):
	from config import ise_username
	from config import ise_password
	from app import unnuke_from_space
	#nukeFromSpace(ise_username, ise_password, mac)
	print (mac)
	hosts_db.update({'quarantine': 'False'}, querydb.mac == mac)
	return render_template('response.html', hosts=hosts_db)

#Process for sending blocked domain to Umbrella
@app.route('/block/<string:domain_name>', methods=['POST'])
def block_with_umbrella(domain_name):
	from app import blockWithUmbrella
	from app import umbrella_key
	#blockWithUmbrella(umbrella_key, domain)
	domain_details = domains_db.search(querydb.domain == domain_name)
	print (domain_name)
	return render_template('domain_research.html', domain=domain_details)

@app.route('/research', methods=['GET', 'POST'])
def research():
	if request.method == 'GET':
		return render_template('research.html', hosts=hosts_db)
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/research/domains/<domain_name>')
def research_domain(domain_name):
	domain_details = domains_db.search(querydb.domain == domain_name)
	print (domain_details)
	if request.method == 'GET':
		return render_template('domain_research.html', domain=domain_details)
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/research/malware/<threat_name>')
def research_malware(threat_name):
	threat_details = threats_db.search(querydb.sha256 == threat_name)
	print (threat_details)
	if request.method == 'GET':
		return render_template('threat_research.html', threat=threat_details)
	else:
		return "<h2> Invalid Request </h2>"

@app.route('/reports', methods = ['GET', 'POST'])
def reports():
	if request.method == 'POST':
		from app import create_new_webex_teams_incident_room
		from config import webex_teams_access_token
		result = request.form
		incident = {}
		incident_report = open("Incident Report.txt", "w")
		for key, value in result.items():
			incident[key] = value
			incident_report.write(key + ": " + value + "\r\n")
		incident_report.close()
		create_new_webex_teams_incident_room(webex_teams_access_token, incident)
		return render_template('reports.html')

	if request.method == 'GET':
		return render_template('reports.html')
	else:
		return "<h2> Invalid Request </h2>"
