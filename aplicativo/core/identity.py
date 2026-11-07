"""Quem está usando o app: nome para assinaturas e relatórios (sem nomes fixos no código)."""

PLACEHOLDER = '[seu nome]'


def full_name(user):
    """Nome completo cadastrado para a conta, ou '' se não houver."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return ''
    return (user.get_full_name() or '').strip()


def display_name(user):
    """Nome para relatórios: nome completo, ou o usuário de login."""
    return full_name(user) or (user.get_username() if user is not None and getattr(user, 'is_authenticated', False) else '')
