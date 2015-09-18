"""
Wrapper for the neo4j commands.
"""
from sleekxmpp.plugins.base import base_plugin
import logging
from py2neo import neo4j, node, rel
from py2neo.packages.httpstream.http import SocketError
from rdflib.namespace import RDFS
from rhobot.components.configuration import BotConfiguration
from neo_backend.components.enums import GRAPH_URL_KEY, LOGIN_KEY, PASSWORD_KEY
from urlparse import urlparse

logger = logging.getLogger(__name__)


class Neo4jWrapper(base_plugin):
    """
    Wrapper component.
    """
    name = 'neo4j_wrapper'
    description = 'Neo4j Wrapper'
    dependencies = {'xep_0030', 'rho_bot_configuration'}

    def plugin_init(self):
        self._graph = None
        self.xmpp.add_event_handler(BotConfiguration.CONFIGURATION_UPDATED_EVENT, self._reconfigure)
        self.xmpp.add_event_handler(BotConfiguration.CONFIGURATION_RECEIVED_EVENT, self._reconfigure)

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(Neo4jWrapper, self).post_init()
        self._discovery = self.xmpp['xep_0030']
        self._configuration = self.xmpp['rho_bot_configuration']

        self._discovery.add_identity('store', 'neo4j')

    def _reconfigure(self, event):
        """
        Configure the wrapper to connect to the graph.
        :param event:
        :return:
        """
        graph_url = self._configuration.get_value(GRAPH_URL_KEY, None, persist_if_missing=False)
        login = self._configuration.get_value(LOGIN_KEY, None, persist_if_missing=False)
        password = self._configuration.get_value(PASSWORD_KEY, None, persist_if_missing=False)

        if graph_url and login and password:
            result = urlparse(graph_url)
            net_location = result.netloc
            neo4j.authenticate(net_location, login, password)

        if graph_url:
            self._graph = neo4j.Graph()
        else:
            self._graph = None

    def create_node(self, properties=None, types=None, relationships=None):
        """
        Create a new node based on the properties and the types that are provided.
        :param properties:
        :param types:
        :return:
        """
        if self._graph is None:
            raise RuntimeError('Graph not defined')

        if types is None:
            types = []

        if properties is None:
            properties = dict()

        if relationships is None:
            relationships = dict()

        new_node, = self._graph.create(node())

        if len(types):
            new_node.add_labels(*types)

        self.update_node(new_node, properties=properties, relationships=relationships)

        return new_node

    def update_node(self, node_obj, relationships=None, properties=None):
        """
        Update the data stored in the node.
        :param node_obj: node to update.
        :param relationships: relationships to set to the node
        :param properties: properties to set to the node
        :return:
        """
        if self._graph is None:
            raise RuntimeError('Graph not defined')

        if relationships is None:
            relationships = dict()

        if properties is None:
            properties = dict()

        for rel_type, nodes in relationships.iteritems():

            if isinstance(nodes, basestring):
                nodes = [nodes]

            # See if the relationship exists already.
            for end_node_uri in nodes:
                end_node = self.get_node(end_node_uri)

                matched_relationship = list(node_obj.match(rel_type=rel_type, other_node=end_node))

                if not len(matched_relationship):
                    self._graph.create(rel(node_obj, rel_type, end_node))

        for key, value in properties.iteritems():

            stored_value = node_obj.properties.get(key, [])

            if isinstance(value, basestring):
                value = [value]

            stored_value = stored_value + value

            node_obj.properties[key] = set(stored_value)

        node_obj.push()

        return node_obj

    def get_node(self, uri, create=True):
        """
        Fetches the data of a node from uri provided.  If the node is a remote node, then it will attempt to find a
        resource node that has the see Also property of the uri.  If that node doesn't exist, it will create it and
        return it to the calling method.

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
        if self._graph is None:
            raise RuntimeError('Graph not defined')

        if uri.startswith(str(self._graph.uri)):
            node_obj = neo4j.Node()
            node_obj.bind(uri)
            node_obj.pull()
        else:
            properties = {RDFS.seeAlso.toPython(): uri}
            # Find a node that is marked as being a resource with the see also property of the uri
            nodes = self.find_nodes(labels=[RDFS.Resource.toPython()], **properties)
            if len(nodes):
                node_obj = nodes[0]
            elif create:
                node_obj = self.create_node(properties=properties, types=[RDFS.Resource.toPython()])
            else:
                node_obj = None

        return node_obj

    def find_nodes(self, labels=None, **kwargs):
        """
        Find a list of nodes that match the properties provided.
        :param labels:
        :param kwargs:
        :return:
        """
        if self._graph is None:
            raise RuntimeError('Graph not defined')

        if labels is None:
            raise NotImplementedError('All nodes must have a label')

        nodes = self._graph.find(labels[0])

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

    def execute_cypher(self, query):
        """
        Execute the query and return a list of the results that are provided.
        :param query: query to execute.
        :return:
        """
        if self._graph is None:
            raise RuntimeError('Graph not defined')

        results = self._graph.cypher.execute(statement=query)

        if results.records:
            return results

        return None

    @property
    def connected(self):
        """
        Test the connection to the graph.
        :return:
        """
        try:
            graph_size = self._graph.size
            return graph_size >= 0
        except SocketError:
            return False
        except AttributeError:
            return False


neo4j_wrapper = Neo4jWrapper
