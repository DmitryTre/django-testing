# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify
from notes.forms import WARNING
from notes.models import Note

from .paths_file import URL_REVERSE, BaseTest

User = get_user_model()


class TestLogic(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
            'author': 'author'
        }

    def test_anonymous_user_cant_create_note(self):
        current_count = list(Note.objects.all())
        response = self.client.post(URL_REVERSE.add, data=self.form_data)
        expected_url = f'{URL_REVERSE.login}?next={URL_REVERSE.add}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(list(Note.objects.all()), current_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(
            URL_REVERSE.add,
            data=self.form_data
        )
        self.assertRedirects(response, URL_REVERSE.success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(
            URL_REVERSE.add,
            data=self.form_data
        )
        self.assertRedirects(response, URL_REVERSE.success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        initial_notes = list(Note.objects.values_list('pk', flat=True))
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            URL_REVERSE.add,
            data=self.form_data
        )
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING
        )
        current_notes = Note.objects.values_list('pk', flat=True)
        self.assertEqual(set(initial_notes), set(current_notes))

    def test_author_can_delete_note(self):
        initial_notes = list(Note.objects.values_list('pk', flat=True))
        response = self.author_client.delete(URL_REVERSE.delete)
        self.assertRedirects(response, URL_REVERSE.success)
        self.assertEqual(Note.objects.count(), len(initial_notes) - 1)

    def test_user_cant_delete_note_of_another_user(self):
        initial_notes = list(Note.objects.values_list('pk', flat=True))
        response = self.another_author_client.delete(URL_REVERSE.delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        current_notes = Note.objects.values_list('pk', flat=True)
        self.assertEqual(set(initial_notes), set(current_notes))
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            URL_REVERSE.edit,
            data=self.form_data
        )
        self.assertRedirects(response, URL_REVERSE.success)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_author_client.post(
            URL_REVERSE.edit,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)
