from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .content import (ADD_NOTE_URL, SUCCESS_URL, EDIT_URL, DELETE_URL,
                      EXPECTED_ANONYM_TO_LOGIN, BaseTest)


class TestLogic(BaseTest):

    def test_anonymous_user_cant_create_note(self):
        notes = set(Note.objects.all())
        self.assertRedirects(self.client.post(
            ADD_NOTE_URL,
            data=self.form_data),
            EXPECTED_ANONYM_TO_LOGIN
        )
        self.assertEqual(set(Note.objects.all()), notes)

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
        notes = Note.objects.values_list('pk', flat=True)
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
            set(notes),
            set(Note.objects.values_list('pk', flat=True))
        )

    def test_author_can_delete_note(self):
        notes = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertEqual(Note.objects.count(), notes - 1)

    def test_user_cant_delete_note_of_another_user(self):
        current_notes = Note.objects.values_list('pk', flat=True)
        response = self.another_author_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(
            set(Note.objects.values_list('pk', flat=True)),
            set(current_notes)
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_author_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)
