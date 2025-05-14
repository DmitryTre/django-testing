from http import HTTPStatus

from django.contrib.auth import get_user_model

from .paths_file import URL_REVERSE, BaseTest

User = get_user_model()


class TestRoutes(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_pages_availability_for_all(self):
        user_statuses = (
            (URL_REVERSE.home, self.client, HTTPStatus.OK),
            (URL_REVERSE.login, self.client, HTTPStatus.OK),
            (URL_REVERSE.logout, self.client, HTTPStatus.OK),
            (URL_REVERSE.login, self.client, HTTPStatus.OK),
            (URL_REVERSE.signup, self.client, HTTPStatus.OK),
            (URL_REVERSE.add, self.another_author_client, HTTPStatus.OK),
            (URL_REVERSE.success, self.another_author_client, HTTPStatus.OK),
            (URL_REVERSE.list, self.another_author_client, HTTPStatus.OK),
            (URL_REVERSE.detail, self.author_client, HTTPStatus.OK),
            (URL_REVERSE.edit, self.author_client, HTTPStatus.OK),
            (URL_REVERSE.delete, self.author_client, HTTPStatus.OK),
            (URL_REVERSE.detail,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
            (URL_REVERSE.edit,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
            (URL_REVERSE.delete,
             self.another_author_client,
             HTTPStatus.NOT_FOUND),
        )

        for url, user, status in user_statuses:
            with self.subTest(url=url, user=user, status=status):
                if url == URL_REVERSE.logout:
                    response = user.post(url)
                else:
                    response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonym(self):
        urls = (
            (URL_REVERSE.detail),
            (URL_REVERSE.edit),
            (URL_REVERSE.delete),
            (URL_REVERSE.add),
            (URL_REVERSE.success),
            (URL_REVERSE.list),
        )

        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{URL_REVERSE.login}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
