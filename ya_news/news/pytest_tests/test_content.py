from django.conf import settings

from news.forms import CommentForm

FORM_DATA = {'text': 'Новый текст'}


def test_home_page(client, home_url, news_with_dates):
    response = client.get(home_url)
    assert len(response.context['object_list']) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, news_with_dates):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_detail_page_contains_form(author_client, news_detail_url):
    response = author_client.get(news_detail_url, data=FORM_DATA)
    form = response.context['form']
    assert 'form' in response.context
    assert isinstance(form, CommentForm)


def test_detail_page_not_contains_form_for_anonym(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_comments_order(client, news, news_detail_url, comments):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    assert all_date_created == sorted(all_date_created)
