from datetime import timedelta
import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    return News.objects.create(
        title='Заголовок',
        text='Текст новости')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(text='Текст комментария',
                                  news=news, author=author)


@pytest.fixture
def comments(author, news):
    for index in range(222):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_with_dates():
    today = timezone.now()
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def expected_login_url(login_url, news_detail_url):
    return f'{login_url}?next={news_detail_url}'


@pytest.fixture
def expected_comment_success_url(news_detail_url):
    return f'{news_detail_url}#comments'


@pytest.fixture
def redirect_edit_url(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def redirect_delete_url(login_url, delete_url):
    return f'{login_url}?next={delete_url}'
