"""
Command that will execute a provided cypher command.
"""
import logging
import json
from neo_backend import command_handler
from rhobot.components.commands.base_command import BaseCommand
from rhobot.components.storage.enums import Commands, CypherFlags
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.namespace import NEO4J
from rdflib.namespace import RDF


logger = logging.getLogger(__name__)


class ExecuteCypher(BaseCommand):
    """
    Neo4j Storage plugin for finding data.
    """
    name = Commands.CYPHER.value
    description = 'Neo4j Execute Cypher'
    dependencies = BaseCommand.default_dependencies.union({'xep_0030', 'xep_0122'})

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(ExecuteCypher, self).post_init()
        self._discovery = self.xmpp['xep_0030']

        self._discovery.add_identity('store', 'neo4j')

    def command_start(self, request, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        payload = StoragePayload(initial_session['payload'])
        cypher_statement = payload.properties.get(str(NEO4J.cypher), None)

        if cypher_statement:
            records = command_handler.execute_cypher(cypher_statement[0])
        else:
            records = None

        # Build up the form response containing the newly created uri
        result_collection_payload = ResultCollectionPayload()

        translation_map = CypherFlags.TRANSLATION_KEY.fetch_from(payload.flags)
        translation_map = json.loads(translation_map)

        if records:
            for record in records.records:
                about = None
                labels = None
                columns = {}

                for key, value in translation_map.iteritems():
                    if key == str(RDF.about):
                        node = record[value]
                        about = node.uri
                        labels = node.labels
                    else:
                        columns[key] = record[value]

                result_payload = ResultPayload(about=about, types=labels)

                for key, value in columns.iteritems():
                    result_payload.add_column(key, value)

                result_collection_payload.append(result_payload)

        initial_session['payload'] = result_collection_payload.populate_payload()

        return initial_session

storage_cypher = ExecuteCypher
