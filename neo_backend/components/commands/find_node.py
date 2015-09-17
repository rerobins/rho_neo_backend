"""
Command that will find a specific node based on the details in the payload.
"""
"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging
from neo_backend import command_handler
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.enums import FindFlags, FindResults


logger = logging.getLogger(__name__)

class FindNode(base_plugin):
    """
    Neo4j Storage plugin for finding data.
    """
    name = 'storage_find_node'
    description = 'Neo4j Find Node'
    dependencies = {'xep_0030', 'xep_0050', 'xep_0122'}

    def plugin_init(self):
        self.xmpp.add_event_handler("session_start", self._start)

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        self.xmpp['xep_0030'].add_identity('store', 'neo4j')

    def _start(self, event):
        self.xmpp['xep_0050'].add_command(node=Commands.FIND_NODE.value, name='Find Node',
                                          handler=self._starting_point)

    def _starting_point(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        payload = StoragePayload(initial_session['payload'])

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Find Node iq: %s' % iq)
            logger.debug('Initial_session: %s' % initial_session)
            logger.debug('about: %s' % payload.about)
            logger.debug('relationships: %s' % payload.references)
            logger.debug('properties: %s' % payload.properties)
            logger.debug('types: %s' % payload.types)

        created = False
        nodes = command_handler.find_nodes(payload.types, **payload.properties)

        if not nodes and FindFlags.CREATE_IF_MISSING.fetch_from(payload.flags):
            node = command_handler.create_node(types=payload.types, properties=payload.properties,
                                               relationships=payload.references)
            created = True
            nodes.append(node)

        # Build up the form response containing the newly created uri
        result_collection_payload = ResultCollectionPayload()
        for node in nodes:
            payload = ResultPayload(about=node.uri, types=node.labels)
            if created:
                payload.add_flag(FindResults.CREATED, True)

            result_collection_payload.append(payload)

        initial_session['payload'] = result_collection_payload.populate_payload()

        return initial_session

storage_find_node = FindNode
