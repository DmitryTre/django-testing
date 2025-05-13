from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст'}
BAD_WORDS_DATA = {'text': 'Какой-то текст, {}, еще текст'}


def test_anonym_cant_create_comment(client, news, news_detail_url, login_url):
    comments = list(Comment.objects.all())
    response = client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    new_comments = list(Comment.objects.all())
    assert new_comments == comments


def test_user_can_create_comment(author_client, news, news_detail_url, author):
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assertRedirects(response, f'{news_detail_url}#comments',
                    status_code=HTTPStatus.FOUND)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_words_list',
    BAD_WORDS
)
def test_user_cant_use_bad_words(author_client,
                                 bad_words_list,
                                 news_detail_url,
                                 news):
    bad_words_data = BAD_WORDS_DATA['text'].format(bad_words_list)
    response = author_client.post(news_detail_url,
                                  data={'text': bad_words_data})
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client,
                                   news_detail_url,
                                   delete_url,
                                   create_comment):
    comments_count = Comment.objects.count()
    comment_id = create_comment.id
    url_to_comments = news_detail_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(id=comment_id)


def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  delete_url,
                                                  create_comment):
    comments_count = list(Comment.objects.all())
    saved_comment = create_comment
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert list(Comment.objects.all()) == comments_count
    assert Comment.objects.filter(id=saved_comment.id).exists()


def test_author_can_edit_comment(author_client,
                                 news_detail_url,
                                 edit_url,
                                 create_comment):
    url_to_comments = news_detail_url + '#comments'
    response = author_client.post(edit_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    edited_comment = Comment.objects.get(id=create_comment.id)
    assert edited_comment.text == FORM_DATA['text']
    assert edited_comment.author == create_comment.author


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        edit_url,
        create_comment
):
    original_text = create_comment.text
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=create_comment.id)
    assert updated_comment.text == original_text
