"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging
from rdflib.namespace import RDFS, RDF
from neo_backend import command_handler
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload

logger = logging.getLogger(__name__)

class UpdateNode(base_plugin):
    """
    Neo4j Storage plugin for storing data.
    """
    name = 'storage_update_node'
    description = 'Neo4j Update Node'
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
        self.xmpp['xep_0050'].add_command(node=Commands.UPDATE_NODE.value, name='Update Node',
                                          handler=self._starting_point)

    def _starting_point(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        logger.info('Update Node iq: %s' % iq)
        logger.info('Initial_session: %s' % initial_session)

        payload = StoragePayload(initial_session['payload'])

        logger.debug('relationships: %s' % payload.references())
        logger.debug('properties: %s' % payload.properties())
        logger.debug('types: %s' % payload.types())
        logger.debug('about: %s' % payload.about)

        node = command_handler.get_node(payload.about)

        command_handler.update_node(node, payload.references(), payload.properties())

        # Build up the form response containing the newly created uri
        result = ResultCollectionPayload(self.xmpp['xep_0004'].make_form())
        result.append(ResultPayload(about=str(node.uri), types=node.labels))

        initial_session['payload'] = result.populate_payload()

        return initial_session

storage_update_node = UpdateNode
