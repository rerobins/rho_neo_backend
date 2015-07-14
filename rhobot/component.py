import logging

logger = logging.getLogger(__name__)

class BaseComponent(object):

    def __init__(self):
        """
        Initialize this component.
        :return:
        """
        self.xmpp = None

    def configure(self, xmpp):
        """
        Configure this module.
        :param xmpp:
        :return:
        """
        self.xmpp = xmpp

        self._configure()

    def _configure(self):
        """
        Overridden to configure the module.
        :return:
        """
