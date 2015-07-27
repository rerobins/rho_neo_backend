"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging
from rdflib.namespace import RDFS, RDF
from neo_backend import command_handler
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage_client import CREATE_NODE_COMMAND

logger = logging.getLogger(__name__)

class CreateNode(base_plugin):
    """
    Neo4j Storage plugin for storing data.
    """
    name = 'storage_create_node'
    description = 'Neo4j Create Node'
    dependencies = {'xep_0030', 'xep_0050'}

    def plugin_init(self):
        self.xmpp.add_event_handler("session_start", self._start)

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        self.xmpp['xep_0030'].add_identity('store', 'neo4j')

    def _start(self, event):
        self.xmpp['xep_0050'].add_command(node=CREATE_NODE_COMMAND, name='Create Node', handler=self._starting_point)

    def _starting_point(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        logger.info('Create Node iq: %s' % iq)
        logger.info('Initial_session: %s' % initial_session)

        relationships = {}
        properties = {}
        types = []

        # Parse the Fields
        fields = initial_session['payload']['fields']
        for field_key in fields:
            field = fields[field_key]
            variable = field['var']
            vtype = field['type']
            value = field['value']

            logger.debug('field: %s' % fields[field_key])
            logger.debug('  type: %s' % vtype)
            logger.debug('  var: %s' % variable)
            logger.debug('  value: %s' % value)

            if vtype == RDFS.Resource.toPython():
                _storage_helper(relationships, variable, value)
            elif vtype == RDFS.Literal.toPython():
                _storage_helper(properties, variable, value)
            elif vtype == RDF.type.toPython():
                if type(value) is list:
                    types = types + value
                else:
                    types.append(value)

        logger.debug('relationships: %s' % relationships)
        logger.debug('properties: %s' % properties)
        logger.debug('types: %s' % types)

        # Create the node
        uri = command_handler.create_node(properties=properties, types=types, relationships=relationships)

        # Build up the form response containing the newly created uri
        form = self.xmpp['xep_0004'].make_form()
        form.add_reported(var=RDF.about.toPython(), ftype=RDFS.Resource.toPython())
        form.add_item({RDF.about.toPython(): str(uri)})

        initial_session['payload'] = form

        return initial_session

def _storage_helper(dictionary, key, value):
    """
    Helper that will put all of the values into a list inside the dictionary.
    :param dictionary:
    :param key:
    :param value:
    :return:
    """
    storage = dictionary.get(key, [])
    if type(value) is list:
        storage = storage + value
    else:
        storage.append(value)
    dictionary[key] = storage

storage_create_node = CreateNode
