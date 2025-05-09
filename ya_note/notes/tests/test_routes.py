from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.client_author = Client()
        cls.client_reader = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='slug'
        )

    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
            'users:logout'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)  # Изменяем метод на POST
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_accessibility_for_author_and_reader(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in (('notes:detail', (self.note.slug,)),
                           ('notes:edit', (self.note.slug,)),
                           ('notes:delete', (self.note.slug,)),
                           ('notes:add', None),
                           ('notes:success', None),
                           ('notes:list', None),):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
