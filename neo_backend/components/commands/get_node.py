"""
Module that will contain the work flow for fetching a node from the database.
"""
import logging
from neo_backend import command_handler
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload
from sleekxmpp.plugins.xep_0004 import FormField
from rhobot.components.stanzas.rdf_stanza import RDFType
from sleekxmpp.xmlstream import register_stanza_plugin


logger = logging.getLogger(__name__)

class GetNode(base_plugin):
    """
    Neo4j Storage plugin for finding data.
    """
    name = 'storage_get_node'
    description = 'Neo4j Get Node'
    dependencies = {'xep_0030', 'xep_0050'}

    def plugin_init(self):
        self.xmpp.add_event_handler("session_start", self._start)
        register_stanza_plugin(FormField, RDFType)

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        self.xmpp['xep_0030'].add_identity('store', 'neo4j')

    def _start(self, event):
        self.xmpp['xep_0050'].add_command(node=Commands.GET_NODE.value, name='Get Node',
                                          handler=self._starting_point)

    def _starting_point(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        logger.info('Get Node iq: %s' % iq)
        logger.info('Initial_session: %s' % initial_session)

        payload = StoragePayload(initial_session['payload'])

        logger.debug('about: %s' % payload.about)

        node = command_handler.get_node(payload.about, create=False)

        result_payload = StoragePayload()
        result_payload.about = node.uri

        # Get the types into place.
        for label in node.labels:
            result_payload.add_type(label)

        # Gather up all of the references
        for relationship in node.match_outgoing():
            result_payload.add_reference(relationship.type, relationship.end_node.uri)

        # Gather up all of the properties
        for key, value in node.properties.iteritems():
            if isinstance(value, list):
                for val in value:
                    result_payload.add_property(key, val)
            else:
                result_payload.add_property(key, value)

        initial_session['payload'] = result_payload.populate_payload()

        return initial_session

storage_get_node = GetNode
