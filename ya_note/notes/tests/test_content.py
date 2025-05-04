from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Автор')
        cls.another_author = User.objects.create(username='Другой автор')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_authors(self):
        url = reverse('notes:list')
        test_cases = (
            (self.author_client, True),
            (self.another_author_client, False)
        )

        for client, expected in test_cases:
            for client, expected in test_cases:
                with self.subTest(client=client):
                    response = client.get(url)
                    object_list = response.context['object_list']
                    self.assertIs(
                        self.note in object_list,
                        expected
                    )

    def test_pages_contains_form(self):
        url_checks_form = [
            reverse('notes:add'),
            reverse('notes:edit', args=[self.note.slug]),
        ]

        for url in url_checks_form:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
