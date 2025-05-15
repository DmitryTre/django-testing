from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .content import (ADD_NOTE_URL, SUCCESS_URL, EDIT_URL, DELETE_URL,
                      EXPECTED_ANONYM_TO_LOGIN, BaseTest)

User = get_user_model()


class TestLogic(BaseTest):

    def test_anonymous_user_cant_create_note(self):
        current_count = set(Note.objects.all())
        response = self.client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, EXPECTED_ANONYM_TO_LOGIN)
        self.assertEqual(set(Note.objects.all()), current_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(
            ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertRedirects(response, SUCCESS_URL)
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
            ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_note_slug_unique(self):
        initial_notes = Note.objects.values_list('pk', flat=True)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING
        )
        self.assertEqual(
            set(initial_notes),
            set(Note.objects.values_list('pk', flat=True))
        )

    def test_author_can_delete_note(self):
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=self.note.pk)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_author_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        current_notes = Note.objects.values_list('pk', flat=True)
        self.assertEqual(set(Note.objects.values_list('pk', flat=True)),
                         set(current_notes))
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_author_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)
