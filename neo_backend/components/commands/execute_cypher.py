"""
Command that will execute a provided cypher command.
"""
import logging
from neo_backend import command_handler
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.namespace import NEO4J


logger = logging.getLogger(__name__)


class ExecuteCypher(base_plugin):
    """
    Neo4j Storage plugin for finding data.
    """
    name = 'storage_cypher'
    description = 'Neo4j Find Node'
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
        self.xmpp['xep_0050'].add_command(node=Commands.CYPHER.value, name='Cypher Query',
                                          handler=self._starting_point)

    def _starting_point(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        payload = StoragePayload(initial_session['payload'])
        cypher_statement = payload.properties().get(str(NEO4J.cypher), None)

        if cypher_statement:
            nodes = command_handler.execute_cypher(cypher_statement[0])
        else:
            nodes = []

        # Build up the form response containing the newly created uri
        result_collection_payload = ResultCollectionPayload(self.xmpp['xep_0004'].make_form())
        for node in nodes:
            result_collection_payload.append(ResultPayload(about=node.uri, types=node.labels))

        initial_session['payload'] = result_collection_payload.populate_payload()

        return initial_session

storage_cypher = ExecuteCypher
