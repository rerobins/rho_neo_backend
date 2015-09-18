"""
Additional components for the neo4j backend.
"""
from neo_backend.components.neo4j_wrapper import neo4j_wrapper

from sleekxmpp.plugins.base import register_plugin


def load_components():
    register_plugin(neo4j_wrapper)
