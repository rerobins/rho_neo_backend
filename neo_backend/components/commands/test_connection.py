"""
Should test the connection to see if it is connected.
"""
from rhobot.components.commands.base_command import BaseCommand


class TestConnection(BaseCommand):

    name = 'test_connection'
    description = 'Test Connection'
    dependencies = BaseCommand.default_dependencies.union({'neo4j_wrapper'})

    def post_init(self):
        super(TestConnection, self).post_init()

        self._neo4j_wrapper = self.xmpp['neo4j_wrapper']

    def command_start(self, request, initial_session):
        """
        Check to see if the graph is connected.
        :param request:
        :param initial_session:
        :return:
        """
        form = self._forms.make_form(ftype='result')
        form.add_reported(var='connected', label='Connected', type='boolean')

        result = self._neo4j_wrapper.connected

        form.add_item({'connected': result})

        initial_session['payload'] = form
        initial_session['next'] = None
        initial_session['has_next'] = False

        return initial_session

test_connection = TestConnection
