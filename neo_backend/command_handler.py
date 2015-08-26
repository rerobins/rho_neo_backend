"""
This module will handle the data manipulations for storing the data in database backend.


Get or create a node based on properties/keys.
Update node based on new properties.
Update node relationships (if it doesn't already exist).
Look up nodes based on properties and queries.

Store all of the properties on a node in a set, that way can maintain all of the values for a given property.

Payload should be organized as:

No.  Will do it this way:

<x xmlns='jabber:x:data' type='submit'>
    <field var='rdf:property' type='text-single'>
        <value>Value</value>
    </field>
    <field var='rdf:resource' type='jid-sing'>
        <value>relationship_value</value>
    </field>
</x>


"""
import logging
from py2neo import neo4j, node, rel
from rdflib.namespace import RDFS, RDF

logger = logging.getLogger(__name__)

# TODO: Allow for configuration of the database.
_graph = neo4j.Graph()


def create_node(properties=None, types=None, relationships=None):
    """
    Create a new node based on the properties and the types that are provided.
    :param properties:
    :param types:
    :return:
    """

    if types is None:
        types = []

    if properties is None:
        properties = dict()

    if relationships is None:
        relationships = dict()

    new_node, = _graph.create(node())

    if len(types):
        new_node.add_labels(*types)

    update_node(new_node, properties=properties, relationships=relationships)

    return new_node


def update_node(node_obj, relationships=None, properties=None):
    """
    Update the data stored in the node.
    :param node_obj: node to update.
    :param relationships: relationships to set to the node
    :param properties: properties to set to the node
    :return:
    """

    if relationships is None:
        relationships = dict()

    if properties is None:
        properties = dict()

    for rel_type, nodes in relationships.iteritems():

        if isinstance(nodes, basestring):
            nodes = [nodes]

        # See if the relationship exists already.
        for end_node_uri in nodes:
            end_node = get_node(end_node_uri)

            matched_relationship = list(node_obj.match(rel_type=rel_type, other_node=end_node))

            if not len(matched_relationship):
                _graph.create(rel(node_obj, rel_type, end_node))

    for key, value in properties.iteritems():

        stored_value = node_obj.properties.get(key, [])

        if isinstance(value, basestring):
            value = [value]

        stored_value = stored_value + value

        node_obj.properties[key] = set(stored_value)

    node_obj.push()

    return node_obj


def get_node(uri, create=True):
    """
    Fetches the data of a node from uri provided.  If the node is a remote node, then it will attempt to find a resource
    node that has the see Also property of the uri.  If that node doesn't exist, it will create it and return it to
    the calling method.

    The logic for this needs to be the following:
      * If the end node of the relationship is a part of the graph, go ahead and create the relationship as
        the logic below implements.
      * If the end node is not a node in the graph, do a look up for the node based on RDFS:seeAlso property
        * If that node doesn't exist
           * create it,
           * store the relationship
        * Else:
           * store the relationship to the node that was found

    When creating the new resource node, the type of the node should be:
     rdfs:Resource
    and contain the property:
     rdfs:seeAlso - the external link that will be pointed to.

    :param uri: uri of the node in the database.
    :param create: should the node be created if it's not found.
    :return:
    """
    if uri.startswith(str(_graph.uri)):
        node_obj = neo4j.Node()
        node_obj.bind(uri)
        node_obj.pull()
    else:
        properties = {RDFS.seeAlso.toPython(): uri}
        # Find a node that is marked as being a resource with the see also property of the uri
        nodes = find_nodes(labels=[RDFS.Resource.toPython()], **properties)
        if len(nodes):
            node_obj = nodes[0]
        elif create:
            node_obj = create_node(properties=properties, types=[RDFS.Resource.toPython()])
        else:
            node_obj = None

    return node_obj


def find_nodes(labels=None, **kwargs):
    """
    Find a list of nodes that match the properties provided.
    :param labels:
    :param kwargs:
    :return:
    """

    if labels is None:
        raise NotImplementedError('All nodes must have a label')

    nodes = _graph.find(labels[0])

    results = []
    label_set = set(labels)
    label_set_size = len(label_set)

    for node_value in nodes:
        labels = node_value.get_labels().intersection(label_set)
        if len(labels) == label_set_size:
            properties_match = True

            # Contains all of the labels, so need to now check the properties.
            for key, value in kwargs.iteritems():
                stored_value = node_value.properties.get(key, None)

                if isinstance(value, basestring):
                    value = [value]

                # Check to see if the stored_value is a relationship instead
                if stored_value is None:
                    relationships = node_value.match_outgoing(rel_type=key)
                    stored_value = [relationship.end_node.uri for relationship in relationships]

                stored_value_set = set(stored_value)
                value_set = set(value)
                intersection = stored_value_set.intersection(value_set)

                if len(intersection) != len(value_set):
                    properties_match = False

            # Passed all of the tests, add it to the result.
            if properties_match:
                results.append(node_value)

    return results


def execute_cypher(query):
    """
    Execute the query and return a list of the results that are provided.
    :param query: query to execute.
    :return:
    """

    results = _graph.cypher.execute(statement=query)

    if results.records:
        return [n.n for n in results.records]

    return []

