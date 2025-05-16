from notes.forms import NoteForm
from notes.models import Note
from .content import ADD_NOTE_URL, LIST_URL, EDIT_URL, BaseTest


class TestContent(BaseTest):

    def test_notes_list(self):
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)

    def test_another_author_context_list(self):
        self.assertNotIn(
            self.note,
            self.another_author_client
            .get(LIST_URL).context['object_list']
        )

    def test_pages_contains_form(self):
        urls = (ADD_NOTE_URL, EDIT_URL)
        for url in urls:
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(url).context.get('form'), NoteForm
                )
