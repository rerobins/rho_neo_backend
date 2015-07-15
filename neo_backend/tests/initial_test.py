from py2neo import neo4j, node
graph_db = neo4j.Graph("http://localhost:7474/db/data/")


me, = graph_db.create(node(name='Me'))

me.add_labels('http://xmlns.com/foaf/0.1/Person')

some_node = neo4j.Node("http://localhost:7474/db/data/node/0")

print 'some_node: %s' % some_node
