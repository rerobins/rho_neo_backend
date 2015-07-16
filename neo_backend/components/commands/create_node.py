"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging

logger = logging.getLogger(__name__)


def starting_point(iq, initial_session):
    """
    Starting point for creating a new node.
    :param iq:
    :param initial_session:
    :return:
    """
    logger.info('Create Node iq: %s' % iq)
    logger.info('Initial_session: %s' % initial_session)

    fields = initial_session['payload']['fields']
    for field_key in fields:
        logger.info('field: %s' % fields[field_key])

    return initial_session