from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'note-slug'

URL_NAME = namedtuple(
    'URL_NAME', (
        'home',
        'login',
        'logout',
        'signup',
        'add',
        'success',
        'list',
        'detail',
        'edit',
        'delete',
    )
)

URL_REVERSE = URL_NAME(
    reverse('notes:home'),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
    reverse('notes:add'),
    reverse('notes:success'),
    reverse('notes:list'),
    reverse('notes:detail', args=(SLUG,)),
    reverse('notes:edit', args=(SLUG,)),
    reverse('notes:delete', args=(SLUG,)),
)


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
