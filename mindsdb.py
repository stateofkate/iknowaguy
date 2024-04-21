import mindsdb_sdk

#connects to the default part (47334) on localhost
server = mindsdb_sdk.MindsDBServer()

# connects to the specified host and port
server = mindsdb_sdk.connect('localhost', 47334)
