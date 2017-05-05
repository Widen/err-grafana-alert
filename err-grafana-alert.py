import random
import bottle


from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class ErrGrafanaAlert(BotPlugin):
    """
    Accepts Grafana webhook calls and posts alert messages in the chat
    """
    _TOKEN_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(ErrGrafanaAlert, self).activate()

        if 'INSTANCES' not in self:
            self.log.warning("Created 'INSTANCES' persistence key")
            self['INSTANCES'] = {}

    def deactivate(self):
        """
        Triggers on plugin deactivation

        You should delete it if you're not using it to override any default behaviour
        """
        super(ErrGrafanaAlert, self).deactivate()

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {
                'TOKEN_LENGTH': 48,
                }

    def check_configuration(self, configuration):
        """
        Triggers when the configuration is checked, shortly before activation

        Raise a errbot.utils.ValidationException in case of an error

        You should delete it if you're not using it to override any default behaviour
        """
        super(ErrGrafanaAlert, self).check_configuration(configuration)

    @webhook
    def example_webhook(self, incoming_request):
        """A webhook which simply returns 'Example'"""
        return "Example"

    @webhook('/grafana/<token>/alert', raw=True)
    def alert_webhook(self, request, token):

        try:
            self.log.info("Try to find Grafana instance with token {token}".format(token=token))
            instance = self._find_instance_by_token(token)
            self.log.info("Found Grafana instance {name} via {token}".format(name=instance['name'], token=token))
        except KeyError:
            self.log.exception()
            bottle.abort(403, "Forbidden")

        self.send(
                self.build_identifier(instance['room']),
                'bla bla alerting',
                )

        return 'OK'

    @arg_botcmd('name', type=str, help='name of the Grafana instance')
    @arg_botcmd('--url', type=str, default=None, help='Optional URL to the Grafana instance. Used for additional security check')
    @arg_botcmd('--room', type=str, default=None, help='Defines the room in which the alerts should be posted. Defaults to the current room')
    @arg_botcmd('--show-images', type=bool, default=True)
    def grafana_add(self, mess, name, url=None, room=None, show_images=True):

        if not name:
            return "You need to set at leat a name..."
        elif name in self['INSTANCES']:
            # instance already exists
            return "{name} already exists as Grafana instance.".format(name=name)

        instance = {
                'name': name,
                'token': self._generate_token(),
                'url': url,
                'show_images': True if show_images is True else False,
                'room': room if room else str(mess.to),
                }

        with self.mutable('INSTANCES') as instances:
            instances[name] = instance

        # send registration notification to target room
        self.send(
                self.build_identifier(instance['room']),
                "Registered Grafana instance {name} for {room}".format(name=name, room=instance['room']),
                )

        yield "Successfully registered Grafana instance"
        yield "Please config Grafana to call following webhook: {server}/grafana/{token}/alert".format(server='', token=instance['token'])

    @botcmd
    def grafana_list(self, mess, args):
        yield "{count} Grafana instances found".format(count=len(self['INSTANCES']))

        for name, instance in self['INSTANCES'].items():
            yield "{name} in {room} -> {token}".format(**instance)

    def _generate_token(self, length=None):
        if not length:
            length = self.config.get('TOKEN_LENGTH', 128)

        rand = random.SystemRandom()
        token = []
        for i in range(0, length):
            token.append(self._TOKEN_ALPHABET[rand.randint(0, len(self._TOKEN_ALPHABET)-1)])

        return ''.join(token)

    def _find_instance_by_token(self, token):

        for name, instance in self['INSTANCES'].items():
            if instance['token'] == token:
                return instance

        raise KeyError("No Grafana instance found with this token {token}".format(token=token))
