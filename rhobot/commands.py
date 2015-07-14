"""
Command Support objects for rhobot.
"""
import logging
from rhobot.component import BaseComponent

logger = logging.getLogger(__name__)


class CommandComponent(BaseComponent):

    def _configure(self):
        self.xmpp.register_plugin('xep_0050')  # AdHoc Commands

        self.xmpp['xep_0050'].add_command(node='greeting', name='Greeting', handler=self._handle_command)

    def _handle_command(self, iq, session):
        session['has_next'] = False

        form = self.xmpp['xep_0004'].makeForm('form', 'Greeting')

        session['form'] = form

        return session
