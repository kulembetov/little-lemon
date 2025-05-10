# Little Lemon Restaurant – Django Web App

A modern, minimalistic Django web application for the fictional Little Lemon Restaurant. This app showcases a Mediterranean menu, allows customers to book tables, and provides a beautiful, responsive user experience with dark/light mode.

---

## Features

- **Menu Listing:** Browse a variety of Mediterranean dishes with images, prices, and descriptions.
- **Menu Item Detail:** View detailed information and a large image for each dish.
- **Booking System:** Book a table with name, email, date, time, and number of guests.
- **Admin Interface:** Manage menu items and bookings via Django admin.
- **Modern UI:** Minimal, appetizing design with dark/light mode toggle.
- **Seed & Clean Scripts:** Easily populate or clear the menu database.

---

## Tech Stack

- **Backend:** Python 3, Django 5
- **Frontend:** Django Templates, HTML5, CSS3 (Inter font, responsive, minimal)
- **Database:** SQLite (default, easy to swap)
- **Other:** Unsplash images for menu items

---

## Setup & Usage

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd little-lemon
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 5. (Optional) Seed the menu with sample data

```bash
python manage.py shell
>>> from restaurant.menu_seed_data import menu_items
>>> from restaurant.models import MenuItem
>>> for item in menu_items:
...     MenuItem.objects.create(**item)
>>> exit()
```

### 6. Start the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the app.

---

## Cleaning the Menu

To remove all menu items from the database:

```bash
python manage.py shell
>>> from restaurant.clean_menu import clean_menu
>>> clean_menu()
>>> exit()
```

---

## Project Structure

- `restaurant/` – Django app with models, views, templates, and utility scripts
- `restaurant/menu_seed_data.py` – Sample menu items for quick DB population
- `restaurant/clean_menu.py` – Script to clear all menu items
- `restaurant/templates/restaurant/` – All HTML templates (home, menu, detail, about, book, base)
- `littlelemon/` – Django project settings and URLs

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details. 