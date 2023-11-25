from django.core.validators import RegexValidator


class HexColorValidator(RegexValidator):
    """Проверка соответствия строки HEX-формату."""

    regex = r'^#[0-9A-Fa-f]{3,6}$'
    message = ('Значение цвета должно быть в HEX-формате: В начале "#", '
               'далее 3-6 символов, каждый из которых является цифрой, '
               'или буквой от A(a) до F(f). Например "#b2b5aa".')
