from __future__ import absolute_import

import json,io
import os
from urlparse import urlparse


import datetime

from flask import Flask, render_template, request, redirect, session
from flask_sslify import SSLify
from rauth import OAuth2Service
import requests

app = Flask(__name__, static_folder='static', static_url_path='')
#app.requests_session = requests.Session()
app.secret_key = os.urandom(24)

sslify = SSLify(app)
tokenRefreshThreshold=864000 #Refresh token is token about to expire in 10 days, 10*24*3600 seconds

with open('config.json') as f:
    config = json.load(f)


def generate_oauth_service():
    """Prepare the OAuth2Service that is used to make requests later."""
    return OAuth2Service(
        client_id=os.environ.get('UBER_CLIENT_ID'),
        client_secret=os.environ.get('UBER_CLIENT_SECRET'),
        name=config.get('name'),
        authorize_url=config.get('authorize_url'),
        access_token_url=config.get('access_token_url'),
        base_url=config.get('base_url'),
    )


def generate_ride_headers(token):
    """Generate the header object that is used to make api requests."""
    return {
        "Authorization": "Bearer %s" % token,
        "Content-Type": "application/json"
    }

def getFareDetails():
    """Example call to the price estimates endpoint.

    Returns the time estimates from the given lat/lng given below.
    """
    url = config.get('base_uber_url') + 'requests/estimate'
    params = {
        'product_id': os.environ.get('UBER_DEFAULT_PRODUCT_ID'),
        'start_latitude': config.get('start_latitude'),
        'start_longitude': config.get('start_longitude'),
        'end_latitude': config.get('end_latitude'),
        'end_longitude': config.get('end_longitude')
    }
    #print params
    #print generate_ride_headers(session.get('access_token'))
    response = requests.post(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        data=json.dumps(params)
    )  
    
    return response.text


def reserveAnUber():
    #Book an Uber based on a fare ID
    fareDetails=getFareDetails();
    data=json.loads(fareDetails)
    fareID=data["fare"]["fare_id"]
    
    url = config.get('base_uber_url') + 'requests'
    params = {
        'fare_id': fareID,
        'product_id': os.environ.get('UBER_DEFAULT_PRODUCT_ID'),
        'start_latitude': config.get('start_latitude'),
        'start_longitude': config.get('start_longitude'),
        'end_latitude': config.get('end_latitude'),
        'end_longitude': config.get('end_longitude')
    }
    #print params
    #print generate_ride_headers(session.get('access_token'))
    response = requests.post(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        data=json.dumps(params)
    )
    return response.text


def getRideStatus():
    #Get the Status of a Ride
    url = config.get('base_uber_url') + 'requests/current'
    
    #print params
    #print generate_ride_headers(session.get('access_token'))
    response = requests.get(
        url,
        #headers=generate_ride_headers(session.get('access_token'))
        headers=generate_ride_headers(getAccessToken()),
        
    )    
    return response.text



@app.route('/bookUber', methods=['GET'])
def bookUber():
    cabStatus=reserveAnUber()
    return cabStatus
    


@app.route('/viewRideStatus', methods=['GET'])
def viewRideStatus():
    rideStatusJson=getRideStatus()
    #data=json.loads(rideStatusJson)
    return rideStatusJson



@app.route('/setRideStatus/<string:rideStatus>', methods=['GET'])
def setRideStatus(rideStatus):
    #Get the Status of a Ride
    
    rideStatusJson=getRideStatus()
    data=json.loads(rideStatusJson)     
    rideID=data["request_id"]
    
    url = config.get('base_uber_url') + 'sandbox/requests/' +rideID
    #print url
    #print rideStatus
    params = {"status": rideStatus}
    
    #print params
    #print generate_ride_headers(session.get('access_token'))
    response = requests.put(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        data=json.dumps(params)
    )    
    return response.text
    

    
@app.route('/health', methods=['GET'])
def health():
    """Check the status of this application."""
    return ';-)'


@app.route('/', methods=['GET'])
def signup():
    """The first step in the three-legged OAuth handshake.

    You should navigate here first. It will redirect to login.uber.com.
    """
    params = {
        'response_type': 'code',
        'redirect_uri': get_redirect_uri(request),
        'scopes': ','.join(config.get('scopes')),
    }
    url = generate_oauth_service().get_authorize_url(**params)
    return redirect(url)


@app.route('/submit', methods=['GET'])
def submit():
    """The other two steps in the three-legged Oauth handshake.

    Your redirect uri will redirect you here, where you will exchange
    a code that can be used to obtain an access token for the logged-in use.
    """
    params = {
        'redirect_uri': get_redirect_uri(request),
        'code': request.args.get('code'),
        'grant_type': 'authorization_code'
    }
    response = requests.post(
        config.get('access_token_url'),
        auth=(
            os.environ.get('UBER_CLIENT_ID'),
            os.environ.get('UBER_CLIENT_SECRET')
        ),
        data=params,
    )
    #session['access_token'] = response.json().get('access_token')
    #session['refresh_token'] = response.json().get('refresh_token')
    #os.putenv('UBER_REFRESH_TOKEN',response.json().get('refresh_token'))
    #print os.environ.get('UBER_REFRESH_TOKEN')
    #file=open("credentials.json","w").close() #erase all contents of the file
    with open('credentials.json', 'w') as outfile:  
        json.dump(response.json(), outfile)
    return "OK"


def getJSONValueFromCredentials(myKey):
    f = open('credentials.json','r')
    message = f.read()       
    jsonObj=json.loads(message)
    f.close()              
    return jsonObj[myKey]

def getAccessToken():
    return getJSONValueFromCredentials("access_token")
    
def modification_date(filename):
    t = os.path.getmtime(filename)
    return t

##@app.route('/lastModified', methods=['GET'])
##def lastModified():
##    return str(modification_date('credentials.json'))
##


@app.route('/hasTokenExpired', methods=['GET'])
def hasTokenExpired():
    fileModifiedOn=modification_date('credentials.json')
    expiryDuration=getJSONValueFromCredentials("expires_in")
    expiryTime=float(fileModifiedOn)+float(expiryDuration)
    currentTime=float(datetime.datetime.utcnow().strftime("%s"))
    if(expiryTime-currentTime<tokenRefreshThreshold):
        return "Yes"
    else:
        return "No"
    #return str(currentTime)
    

@app.route('/demo', methods=['GET'])
def demo():
    """Demo.html is a template that calls the other routes in this example."""
    return render_template('demo.html', token=session.get('refresh_token'))




@app.route('/products', methods=['GET'])
def products():
    """Example call to the products endpoint.

    Returns all the products currently available in San Francisco.
    """
    url = config.get('base_uber_url') + 'products'
    params = {
        'latitude': config.get('start_latitude'),
        'longitude': config.get('start_longitude'),
    }

    response = requests.get(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        params=params,
    )

    if response.status_code != 200:
        return 'There was an error', response.status_code
    return render_template(
        'results.html',
        endpoint='products',
        data=response.text,
    )


@app.route('/time', methods=['GET'])
def time():
    """Example call to the time estimates endpoint.

    Returns the time estimates from the given lat/lng given below.
    """
    url = config.get('base_uber_url') + 'estimates/time'
    params = {
        'start_latitude': config.get('start_latitude'),
        'start_longitude': config.get('start_longitude'),
    }

    response = requests.get(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        params=params,
    )

    if response.status_code != 200:
        return 'There was an error', response.status_code
    return render_template(
        'results.html',
        endpoint='time',
        data=response.text,
    )


@app.route('/price', methods=['GET'])
def price():
    fareDetails=getFareDetails()    
    return render_template(
        'results.html',
        endpoint='price',
        data=fareDetails,
    )
    


    
    


@app.route('/history', methods=['GET'])
def history():
    """Return the last 5 trips made by the logged in user."""
    url = config.get('base_uber_url_v1_1') + 'history'
    params = {
        'offset': 0,
        'limit': 5,
    }

    response = requests.get(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
        params=params,
    )

    if response.status_code != 200:
        return 'There was an error', response.status_code
    return render_template(
        'results.html',
        endpoint='history',
        data=response.text,
    )


@app.route('/me', methods=['GET'])
def me():
    """Return user information including name, picture and email."""
    url = config.get('base_uber_url') + 'me'
    response = requests.get(
        url,
        #headers=generate_ride_headers(session.get('access_token')),
        headers=generate_ride_headers(getAccessToken()),
    )

    if response.status_code != 200:
        return 'There was an error', response.status_code
    return render_template(
        'results.html',
        endpoint='me',
        data=response.text,
    )


def get_redirect_uri(request):
    """Return OAuth redirect URI."""
    parsed_url = urlparse(request.url)
    if parsed_url.hostname == 'localhost':
        return 'http://{hostname}:{port}/submit'.format(
            hostname=parsed_url.hostname, port=parsed_url.port
        )
    return 'https://{hostname}/submit'.format(hostname=parsed_url.hostname)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
