# Ultimatetct.com game server

This code contains websocket/algorithm part of http://ultimatetct.com.
If you are interested in other repo visit http://github.com/nhenezi/ultimatetct.com.

### Dependencies
* python 2.7.5+
* redis-server v2.6.13
* python-redis bindings
* nodejs v0.10.15 and npm
* mongodb v2.4.6

When above dependecies are statistfied, use `npm install` to install additional packages.
For full list of packages please see `package.json`.

### How to run?
If you want to enable AI first start websocket server: `npm start` and then run one of scripts located in `/algo`
directory.
