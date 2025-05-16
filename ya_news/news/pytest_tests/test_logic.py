from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст'}
BAD_WORDS_DATA = {'text': 'Какой-то текст, {}, еще текст'}


def test_anonym_cant_create_comment(
        client,
        news,
        news_detail_url,
        expected_login_url
):
    comments = set(Comment.objects.all())
    response = client.post(news_detail_url, data=FORM_DATA)
    assertRedirects(response, expected_login_url)
    assert set(Comment.objects.all()) == comments


def test_user_can_create_comment(
        author_client,
        news,
        news_detail_url,
        author,
        expected_comment_success_url
):
    assertRedirects(
        author_client.post(news_detail_url, data=FORM_DATA),
        expected_comment_success_url,
        status_code=HTTPStatus.FOUND
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_words_list',
    BAD_WORDS
)
def test_user_cant_use_bad_words(
    author_client,
    bad_words_list,
    news_detail_url,
    news
):
    response = author_client.post(news_detail_url,
                                  data={'text': BAD_WORDS_DATA['text']
                                        .format(bad_words_list)})
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client,
        delete_url,
        expected_comment_success_url,
        comment
):
    comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, expected_comment_success_url)
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        delete_url,
        comment
):
    comments = set(Comment.objects.all())
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert set(Comment.objects.all()) == comments
    assert Comment.objects.filter(id=comment.id).exists()
    fetched_comment = Comment.objects.get(id=comment.id)
    assert fetched_comment.text == comment.text
    assert fetched_comment.author == comment.author
    assert fetched_comment.news == comment.news


def test_author_can_edit_comment(author_client,
                                 expected_comment_success_url,
                                 edit_url,
                                 comment):
    response = author_client.post(edit_url, data=FORM_DATA)
    assertRedirects(response, expected_comment_success_url)
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == FORM_DATA['text']
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        edit_url,
        comment
):
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
