"""
Command that will configure the neo4j connection.
"""
from rhobot.components.commands.base_command import BaseCommand
from neo_backend.components.enums import GRAPH_URL_KEY, LOGIN_KEY, PASSWORD_KEY


class ConfigureNeo4j(BaseCommand):

    name = 'configure_neo4j'
    description = 'Configure NEO4J'
    dependencies = BaseCommand.default_dependencies.union({'rho_bot_configuration'})

    def post_init(self):
        super(ConfigureNeo4j, self).post_init()
        self._configuration = self.xmpp['rho_bot_configuration']

    def command_start(self, request, initial_session):
        """
        Start the command.
        :param request:
        :param initial_session:
        :return:
        """
        graph_url = self._configuration.get_value(GRAPH_URL_KEY, '', persist_if_missing=False)
        login = self._configuration.get_value(LOGIN_KEY, '', persist_if_missing=False)

        form = self._forms.make_form()
        form.add_field(var='url', label='Graph Url', required=True, value=graph_url)
        form.add_field(var='login', label='Login', required=False, value=login)
        form.add_field(var='password', label='Password', required=False, ftype='private')

        initial_session['payload'] = form
        initial_session['next'] = self._store_configuration
        initial_session['has_next'] = False

        return initial_session

    def _store_configuration(self, payload, session):
        """
        Store the configuration details.
        :param payload:
        :param session:
        :return:
        """
        values = payload.get_values()

        storage_dictionary = {
            GRAPH_URL_KEY: values['url']
        }

        if 'login' in values and values['login']:
            storage_dictionary[LOGIN_KEY] = values['login']

        if 'password' in values and values['password']:
            storage_dictionary[PASSWORD_KEY] = values['password']

        self._configuration.merge_configuration(storage_dictionary)

        session['payload'] = None
        session['next'] = None
        session['has_next'] = None

        return session


configure_neo4j = ConfigureNeo4j
