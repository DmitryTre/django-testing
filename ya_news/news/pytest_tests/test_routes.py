import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.contrib.auth import get_user_model

User = get_user_model()

home_url = pytest.lazy_fixture('home_url')
news_detail_url = pytest.lazy_fixture('news_detail_url')
client_url = pytest.lazy_fixture('client')
login_url = pytest.lazy_fixture('login_url')
signup_url = pytest.lazy_fixture('signup_url')
logout_url = pytest.lazy_fixture('logout_url')
edit_url = pytest.lazy_fixture('edit_url')
delete_url = pytest.lazy_fixture('delete_url')
author_client_url = pytest.lazy_fixture('author_client')
reader_client_url = pytest.lazy_fixture('reader_client')
redirect_edit_url = pytest.lazy_fixture('redirect_edit_url')
redirect_delete_url = pytest.lazy_fixture('redirect_delete_url')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    (
        (home_url, client_url, HTTPStatus.OK, 'get'),
        (news_detail_url, client_url, HTTPStatus.OK, 'get'),
        (login_url, client_url, HTTPStatus.OK, 'get'),
        (signup_url, client_url, HTTPStatus.OK, 'get'),
        (logout_url, client_url, HTTPStatus.OK, 'post'),
        (edit_url, author_client_url, HTTPStatus.OK, 'get'),
        (delete_url, author_client_url, HTTPStatus.OK, 'get'),
        (edit_url, reader_client_url, HTTPStatus.NOT_FOUND, 'get'),
        (delete_url, reader_client_url,
         HTTPStatus.NOT_FOUND, 'get'),
        (redirect_delete_url, client_url,
         HTTPStatus.OK, 'get'),
        (redirect_edit_url, client_url,
         HTTPStatus.OK, 'get'),
        (edit_url, client_url, HTTPStatus.FOUND, 'get'),
        (delete_url, client_url, HTTPStatus.FOUND, 'get'),
    )
)
def test_availability(
    url,
    parametrized_client,
    expected_status,
    method
):
    response = getattr(parametrized_client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ('url', 'redirect_anonym_url'),
    (
        (edit_url, redirect_edit_url),
        (delete_url, redirect_delete_url)
    )
)
def test_redirect_for_anonymous_client(client, url, redirect_anonym_url):
    assertRedirects(client.get(url), redirect_anonym_url)
