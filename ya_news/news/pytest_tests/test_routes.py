import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.contrib.auth import get_user_model

User = get_user_model()

home_url_fixture = pytest.lazy_fixture('home_url')
news_detail_url_fixture = pytest.lazy_fixture('news_detail_url')
client_fixture = pytest.lazy_fixture('client')
login_url_fixture = pytest.lazy_fixture('login_url')
signup_url_fixture = pytest.lazy_fixture('signup_url')
logout_url_fixture = pytest.lazy_fixture('logout_url')
edit_url_fixture = pytest.lazy_fixture('edit_url')
delete_url_fixture = pytest.lazy_fixture('delete_url')
author_client_fixture = pytest.lazy_fixture('author_client')
reader_client_fixture = pytest.lazy_fixture('reader_client')
expected_edit_url_fixture = f'{login_url_fixture}?next={edit_url_fixture}'
expected_delete_url_fixture = f'{login_url_fixture}?next={delete_url_fixture}'


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    (
        (home_url_fixture, client_fixture, HTTPStatus.OK, 'get'),
        (news_detail_url_fixture, client_fixture, HTTPStatus.OK, 'get'),
        (login_url_fixture, client_fixture, HTTPStatus.OK, 'get'),
        (signup_url_fixture, client_fixture, HTTPStatus.OK, 'get'),
        (logout_url_fixture, client_fixture, HTTPStatus.OK, 'post'),
        (edit_url_fixture, author_client_fixture, HTTPStatus.OK, 'get'),
        (delete_url_fixture, author_client_fixture, HTTPStatus.OK, 'get'),
        (edit_url_fixture, reader_client_fixture, HTTPStatus.NOT_FOUND, 'get'),
        (delete_url_fixture, reader_client_fixture,
         HTTPStatus.NOT_FOUND, 'get'),
        (expected_delete_url_fixture, client_fixture,
         HTTPStatus.NOT_FOUND, 'get'),
        (expected_edit_url_fixture, client_fixture,
         HTTPStatus.NOT_FOUND, 'get'),
        (edit_url_fixture, client_fixture, HTTPStatus.FOUND, 'get'),
        (delete_url_fixture, client_fixture, HTTPStatus.FOUND, 'get'),
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
        (edit_url_fixture, '/auth/login/?next=/edit_comment/1/'),
        (delete_url_fixture, '/auth/login/?next=/delete_comment/1/')
    )
)
def test_redirect_for_anonymous_client(client, url, redirect_anonym_url):
    assertRedirects(client.get(url), redirect_anonym_url)
