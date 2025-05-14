from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

from .paths_file import URL_REVERSE, BaseTest

User = get_user_model()


class TestContent(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_notes_list(self):
        self.client.force_login(self.author)
        response = self.client.get(URL_REVERSE.list)
        notes = response.context['object_list']
        first_note = notes[0]
        database_note = Note.objects.get(pk=first_note.pk)
        self.assertIn(first_note, notes)
        self.assertEqual(first_note.title, database_note.title)
        self.assertEqual(first_note.text, database_note.text)
        self.assertEqual(first_note.slug, database_note.slug)
        self.assertEqual(first_note.author, database_note.author)

    def test_author_context_list(self):
        self.client.force_login(self.author)
        response = self.client.get(URL_REVERSE.list)
        notes_count = len(response.context['object_list'])
        self.assertEqual(notes_count, 1)

    def test_another_author_context_list(self):
        self.client.force_login(self.another_author)
        response = self.client.get(URL_REVERSE.list)
        notes_count = len(response.context['object_list'])
        self.assertEqual(notes_count, 0)

    def test_pages_contains_form(self):
        urls = (
            URL_REVERSE.add,
            URL_REVERSE.edit,
        )
        for name in urls:
            with self.subTest(name=name):
                self.assertIsInstance(
                    self.author_client.get(name).context.get('form'), NoteForm
                )
