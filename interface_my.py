import vk_api
from config_my import comunity_token, acces_token
from data_store import DataStore

class BotInterface():
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.offset = 0
        self.count = 10
        self.data_store = DataStore()

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    self.offset += self.count
                    users = self.api.search_users(self.params, self.offset - self.count, self.count)
                    if not users:
                        self.message_send(event.user_id, 'нет доступных анкет')
                    else:
                        profile = users.pop()
                        if not self.data_store.check_profile_in_database(profile):
                            self.data_store.add_profile(profile)
                            self.message_send(event.user_id, 'профиль добавлен в базу данных')
                        else:
                            self.message_send(event.user_id, 'профиль уже просмотрен')
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')

    def message_send(self, user_id, message):
        response = self.interface.method('messages.send', {
            'user_id': user_id,
            'random_id': random.randint(1, 2147483647),
            'message': message
        })

    def close_database(self):
        self.data_store.close_database()


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
    bot.close_database()
