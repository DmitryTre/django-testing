from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note
from .content import ADD_NOTE_URL, LIST_URL, EDIT_URL, BaseTest

User = get_user_model()


class TestContent(BaseTest):

    def test_notes_list(self):
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        database_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, database_note.title)
        self.assertEqual(self.note.text, database_note.text)
        self.assertEqual(self.note.slug, database_note.slug)
        self.assertEqual(self.note.author, database_note.author)

    def test_another_author_context_list(self):
        response = self.another_author_client.get(LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_pages_contains_form(self):
        urls = (ADD_NOTE_URL, EDIT_URL)
        for name in urls:
            with self.subTest(name=name):
                self.assertIsInstance(
                    self.author_client.get(name).context.get('form'), NoteForm
                )
