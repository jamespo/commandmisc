natrailmini
===========

Dependencies
------------

* Python 3
* nre-darwin-py


Usage
-----

Get an API key from http://realtime.nationalrail.co.uk/OpenLDBWSRegistration

Get a stations JSON file from https://github.com/fasteroute/national-rail-stations/blob/master/stations.json (cut this down to just the stations you need - see mini-stations.json example)

Create /etc/check_darwin as below:

	[Main]
	wsdl: https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-02-02
	api_key: api-key-you-got


Running
-------

	./natrailmini -j ~/.config/mini-stations.json -f SRA -t LST

