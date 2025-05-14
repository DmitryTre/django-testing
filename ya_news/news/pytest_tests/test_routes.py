import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.parametrize(
    'url_fixture, parametrized_client, expected_status, method',
    (
        (
            pytest.lazy_fixture('home_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('news_detail_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('login_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('signup_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('logout_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK, 'post'
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK, 'get'
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND, 'get'
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND, 'get'
        )
    ),
)
def test_availability(url_fixture,
                      parametrized_client,
                      expected_status,
                      method):
    if method == 'post':
        response = parametrized_client.post(url_fixture)
    else:
        response = parametrized_client.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name', (pytest.lazy_fixture('edit_url'),
             pytest.lazy_fixture('delete_url'),))
def test_redirect_for_anonymous_client(client, login_url, name,):
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
