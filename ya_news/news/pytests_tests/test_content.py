# test_content.py
import pytest

# Импортируем класс формы.
from news.forms import CommentForm
from django.urls import reverse


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, news_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_news_list_for_different_users(
        # Используем фикстуру заметки и параметры из декоратора:
        news, parametrized_client, news_in_list
):
    url = reverse('news:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (news in object_list) is news_in_list


def test_create_news_page_contains_form(author_client):
    url = reverse('news:add')
    # Запрашиваем страницу создания заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)


# В параметры теста передаём фикстуру slug_for_args и клиент с автором заметки:
def test_edit_news_page_contains_form(slug_for_args, author_client):
    url = reverse('news:edit', args=slug_for_args)
    # Запрашиваем страницу редактирования заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    # В качестве параметров передаём name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки
        # никакие дополнительные аргументы для reverse() не нужны.
        ('news:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('news:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)
