from http import HTTPStatus

from django.contrib.auth import get_user_model

from .content import (
    HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL,
    ADD_NOTE_URL, SUCCESS_URL, LIST_URL, DETAIL_URL,
    EDIT_URL, DELETE_URL, EXPECTED_ANONYM_TO_LOGIN,
    REDIRECT_EDIT_URL, REDIRECT_ADD_NOTE_URL,
    REDIRECT_DELETE_URL, REDIRECT_DETAIL_URL,
    REDIRECT_LIST_URL, REDIRECT_SUCCESS_URL, BaseTest
)

User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability_for_all(self):
        user_statuses = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (ADD_NOTE_URL, self.client, HTTPStatus.FOUND),
            (DETAIL_URL, self.client, HTTPStatus.FOUND),
            (ADD_NOTE_URL, self.another_author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.another_author_client, HTTPStatus.OK),
            (LIST_URL, self.another_author_client, HTTPStatus.OK),
            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),
            (DETAIL_URL,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
            (EDIT_URL,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
            (DELETE_URL,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
            (EXPECTED_ANONYM_TO_LOGIN,
             self.client,
             HTTPStatus.OK),
            (LIST_URL, self.client, HTTPStatus.FOUND),
            (ADD_NOTE_URL, self.client, HTTPStatus.FOUND),
            (DELETE_URL, self.client, HTTPStatus.FOUND),
            (EDIT_URL, self.client, HTTPStatus.FOUND),
            (DETAIL_URL, self.client, HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, HTTPStatus.FOUND),
        )

        for url, client, status in user_statuses:
            with self.subTest(url=url, user=client, status=status):
                if url == LOGOUT_URL:
                    response = getattr(client, 'post')(url)
                else:
                    response = getattr(client, 'get')(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonym(self):
        urls = (
            (DETAIL_URL, REDIRECT_DETAIL_URL),
            (EDIT_URL, REDIRECT_EDIT_URL),
            (DELETE_URL, REDIRECT_DELETE_URL),
            (ADD_NOTE_URL, REDIRECT_ADD_NOTE_URL),
            (SUCCESS_URL, REDIRECT_SUCCESS_URL),
            (LIST_URL, REDIRECT_LIST_URL)
        )

        for url, expected_redirect in urls:
            with self.subTest(name=url):
                self.assertRedirects(self.client.get(url), expected_redirect)
