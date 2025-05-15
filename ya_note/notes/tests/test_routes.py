from http import HTTPStatus

from django.contrib.auth import get_user_model

from .content import (HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL,
                      ADD_NOTE_URL, SUCCESS_URL, LIST_URL, DETAIL_URL,
                      EDIT_URL, DELETE_URL, EXPECTED_ANONYM_TO_LOGIN, BaseTest)

User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability_for_all(self):
        user_statuses = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
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
             HTTPStatus.OK)
        )

        for url, user, status in user_statuses:
            with self.subTest(url=url, user=user, status=status):
                if url == LOGOUT_URL:
                    response = user.post(url)
                else:
                    response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonym(self):
        urls = (
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
            ADD_NOTE_URL,
            SUCCESS_URL,
            LIST_URL,
        )

        for name in urls:
            with self.subTest(name=name):
                self.assertRedirects(self.client.get(name),
                                     f'{LOGIN_URL}?next={name}')
