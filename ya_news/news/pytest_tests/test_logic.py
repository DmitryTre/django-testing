# test_logic.py
import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse
from http import HTTPStatus
from news.models import News
# Импортируем функции для проверки редиректа и ошибки формы:
from pytest_django.asserts import assertRedirects, assertFormError

# Импортируем из модуля forms сообщение об ошибке:
from news.forms import WARNING
# Дополнительно импортируем функцию slugify.
from pytils.translit import slugify


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_news(author_client, author, form_data):
    url = reverse('news:add')
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, был выполнен редирект на страницу успешного доб заметки:
    assertRedirects(response, reverse('news:success'))
    # Считаем общее количество заметок в БД, ожидаем 1 заметку.
    assert News.objects.count() == 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_news = News.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_news.title == form_data['title']
    assert new_news.text == form_data['text']
    assert new_news.slug == form_data['slug']
    assert new_news.author == author
    # Вроде бы здесь нарушен принцип "один тест - одна проверка";
    # но если хоть одна из этих проверок провалится -
    # весь тест можно признать провалив., а последующие невые проверки
    # не внесли бы в отчёт о тесте ничего принципиально важного.


# Добавляем маркер, который обеспечит доступ к базе данных:
@pytest.mark.django_db
def test_anonymous_user_cant_create_news(client, form_data):
    url = reverse('news:add')
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert News.objects.count() == 0


# Вызываем фикстуру отдельной заметки, чтобы в базе появилась запись.
def test_not_unique_slug(author_client, news, form_data):
    url = reverse('news:add')
    # Подменяем slug новой заметки на slug уже существующей записи:
    form_data['slug'] = news.slug
    # Пытаемся создать новую заметку:
    response = author_client.post(url, data=form_data)
    # Проверяем, что в ответе содержится ошибка формы для поля slug:
    assertFormError(response, 'form', 'slug', errors=(news.slug + WARNING))
    # Убеждаемся, что количество заметок в базе осталось равным 1:
    assert News.objects.count() == 1


def test_empty_slug(author_client, form_data):
    url = reverse('news:add')
    # Убираем поле slug из словаря:
    form_data.pop('slug')
    response = author_client.post(url, data=form_data)
    # Проверяем, что даже без slug заметка была создана:
    assertRedirects(response, reverse('news:success'))
    assert News.objects.count() == 1
    # Получаем созданную заметку из базы:
    new_news = News.objects.get()
    # Формируем ожидаемый slug:
    expected_slug = slugify(form_data['title'])
    # Проверяем, что slug заметки соответствует ожидаемому:
    assert new_news.slug == expected_slug


# В параметрах вызвана фикстура news: значит, в БД создана заметка.
def test_author_can_edit_news(author_client, form_data, news):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=(news.slug,))
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    assertRedirects(response, reverse('news:success'))
    # Обновляем объект заметки news: получаем обновлённые данные из БД:
    news.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert news.title == form_data['title']
    assert news.text == form_data['text']
    assert news.slug == form_data['slug']


def test_other_user_cant_edit_news(not_author_client, form_data, news):
    url = reverse('news:edit', args=(news.slug,))
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    news_from_db = News.objects.get(id=news.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert news.title == news_from_db.title
    assert news.text == news_from_db.text
    assert news.slug == news_from_db.slug


def test_author_can_delete_news(author_client, slug_for_args):
    url = reverse('news:delete', args=slug_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse('news:success'))
    assert News.objects.count() == 0


def test_other_user_cant_delete_news(not_author_client, slug_for_args):
    url = reverse('news:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert News.objects.count() == 1
