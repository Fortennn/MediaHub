# Sakura Media

Повноцінний каталог фільмів/серіалів/аніме на Django з переглядом, рейтингами та списками перегляду.

## Основні можливості
- Аутентифікація: email/пароль + Google OAuth2 (обовʼязково задати `GOOGLE_OAUTH_CLIENT_ID` і `GOOGLE_OAUTH_CLIENT_SECRET`).
- Профіль користувача: аватар, зміна ніку, статистика, останні відгуки та список перегляду.
- Каталог: фільми/серіали/аніме, жанри, постери, трейлери, фільтри за типом/жанром, сортування (дата, рейтинг, назва), пагінація.
- Рейтинги та коментарі: оцінки 1–10, коментарі, власні оцінки можна редагувати/видаляти.
- Список перегляду: статуси "Заплановано", "Переглянуто", "Улюблене"; окремі сторінки та швидка зміна статусу.
- Пошук: повнотекстовий по назві, оригінальній назві та опису, підказки (autocomplete) у JSON.
- Адмінка (django-jet): управління користувачами, профілями, медіаконтентом, жанрами, сезонами, рейтинґами; превʼю постерів та аватарів.

## Швидкий старт (локально)
1) Встановити залежності:
   ```bash
   pip install -r requirements.txt
   ```
2) Налаштувати змінні середовища:
   - `GOOGLE_OAUTH_CLIENT_ID` — Client ID з Google Cloud (тип Web application).
   - `GOOGLE_OAUTH_CLIENT_SECRET` — Client Secret.
   - Додати redirect URI: `http://127.0.0.1:8000/oauth/complete/google-oauth2/`.
3) Міграції та старт:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # опційно
   python manage.py runserver
   ```
4) Медія/статика:
   - Статичні файли: `static/` (у проді збирати у `staticfiles/`).
   - Аватари/постери: `media/` (аватари у `media/avatars/`).

## Ключові модулі
- `catalog/models.py` — жанри, медіа, сезони, рейтинги, watchlist, профіль користувача.
- `catalog/views.py` — домашня, каталог, деталі, пошук, watchlist, профіль, коментарі.
- `templates/catalog/*` — сторінки каталогу, профілю, пошуку тощо.
- `mediacenter/settings.py` — налаштування Django, соцлогін, статика/медіа.

## OAuth2 (Google)
- Обовʼязково задати `GOOGLE_OAUTH_CLIENT_ID` та `GOOGLE_OAUTH_CLIENT_SECRET` перед запуском.
- Для продакшн-домену додати redirect URI: `https://fortennn.pythonanywhere.com/oauth/complete/google-oauth2/`.

## Корисні команди
- Заповнити міграції: `python manage.py migrate`
- Створити адміна: `python manage.py createsuperuser`
- Запустити локально: `python manage.py runserver`

## Примітки
- При зміні аватара старий файл видаляється автоматично.
- Адмін може редагувати аватар у формі користувача (Користувачі → користувач → поле Avatar).
- Дублікати акаунтів при Google-вході не створюються, якщо email збігається (`SOCIAL_AUTH_ASSOCIATE_BY_EMAIL = True`).
