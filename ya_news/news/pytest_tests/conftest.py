from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from django.test.client import Client
from news.models import Comment, News


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
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости')
    return news


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(text='Текст комментария',
                                  news=news, author=author)


@pytest.fixture
def all_news(author):
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.')
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(author, news):
    all_comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()
        all_comments.append(comment)
    return all_comments


@pytest.fixture
def news_with_dates():
    today = timezone.now()
    News.objects.bulk_create([
        News(title=f'Новость {index}', text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def id_news(news):
    return news.id,


@pytest.fixture
def id_comment(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }
