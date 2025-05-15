from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'note-slug'

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LIST_URL = reverse('notes:list')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
EXPECTED_ANONYM_TO_LOGIN = f'{LOGIN_URL}?next={ADD_NOTE_URL}'


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_author = User.objects.create(username='Другой автор')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        cls.login_url = LOGIN_URL

    def get_redirect_url(self, name):
        return f'{self.login_url}?next={name}'
