# Jinja items collision fix

Jinja resolves `.items` on dictionaries as the built-in `dict.items` method. The templates now use bracket notation for translation keys named `items`.

Replace:

- templates/home.html
- templates/hobbies.html
