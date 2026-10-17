"""Locale-aware, safe messages for application errors."""
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlsplit

from i18n import LANGUAGES
from localization import LOCALES, PHRASES


ERRORS = {
    400: {
        'fr': "La demande n’a pas pu être traitée. Réessayez.",
        'en': 'The request could not be completed. Please try again.',
        'pt-BR': 'Não foi possível concluir a solicitação. Tente novamente.',
        'es': 'No se pudo completar la solicitud. Inténtalo de nuevo.',
    },
    401: {
        'fr': 'Connectez-vous pour continuer.',
        'en': 'Please sign in to continue.',
        'pt-BR': 'Faça login para continuar.',
        'es': 'Inicia sesión para continuar.',
    },
    403: {
        'fr': "Vous n’êtes pas autorisé à effectuer cette action.",
        'en': 'You are not allowed to do that.',
        'pt-BR': 'Você não tem autorização para fazer isso.',
        'es': 'No tienes permiso para hacer eso.',
    },
    404: {
        'fr': 'La page ou le contenu demandé est introuvable.',
        'en': 'The requested page or content could not be found.',
        'pt-BR': 'A página ou o conteúdo solicitado não foi encontrado.',
        'es': 'No se encontró la página o el contenido solicitado.',
    },
    409: {
        'fr': 'Cette demande entre en conflit avec des données existantes.',
        'en': 'This request conflicts with existing information.',
        'pt-BR': 'Esta solicitação entra em conflito com informações existentes.',
        'es': 'Esta solicitud entra en conflicto con información existente.',
    },
    413: {
        'fr': 'La demande dépasse la taille autorisée.',
        'en': 'The request exceeds the allowed size.',
        'pt-BR': 'A solicitação excede o tamanho permitido.',
        'es': 'La solicitud supera el tamaño permitido.',
    },
    422: {
        'fr': 'Certaines informations sont invalides. Vérifiez les champs et réessayez.',
        'en': 'Some information is invalid. Check the fields and try again.',
        'pt-BR': 'Algumas informações são inválidas. Confira os campos e tente novamente.',
        'es': 'Algunos datos no son válidos. Revisa los campos e inténtalo de nuevo.',
    },
    429: {
        'fr': 'Trop de demandes. Réessayez plus tard.',
        'en': 'Too many requests. Please try again later.',
        'pt-BR': 'Muitas solicitações. Tente novamente mais tarde.',
        'es': 'Hay demasiadas solicitudes. Inténtalo más tarde.',
    },
    500: {
        'fr': 'Une erreur est survenue. Réessayez plus tard.',
        'en': 'Something went wrong. Please try again later.',
        'pt-BR': 'Ocorreu um erro. Tente novamente mais tarde.',
        'es': 'Se produjo un error. Inténtalo de nuevo más tarde.',
    },
    502: {
        'fr': 'Le service est temporairement indisponible. Réessayez plus tard.',
        'en': 'The service is temporarily unavailable. Please try again later.',
        'pt-BR': 'O serviço está temporariamente indisponível. Tente novamente mais tarde.',
        'es': 'El servicio no está disponible temporalmente. Inténtalo más tarde.',
    },
    503: {
        'fr': 'Le service est temporairement indisponible. Réessayez plus tard.',
        'en': 'The service is temporarily unavailable. Please try again later.',
        'pt-BR': 'O serviço está temporariamente indisponível. Tente novamente mais tarde.',
        'es': 'El servicio no está disponible temporalmente. Inténtalo más tarde.',
    },
}

BACK_LABELS = {
    'fr': 'Retour au site',
    'en': 'Back to the site',
    'pt-BR': 'Voltar ao site',
    'es': 'Volver al sitio',
}


def _locale(value):
    value = (value or '').strip()
    if value in LANGUAGES:
        return value
    base = value.split('-', 1)[0].lower()
    return {'fr': 'fr', 'en': 'en', 'pt': 'pt-BR', 'es': 'es'}.get(base)


def locale_from_scope(scope):
    """Resolve a supported locale from a request scope, defaulting safely to French."""
    headers = {key.lower(): value for key, value in scope.get('headers', [])}
    chosen = _locale(headers.get(b'x-geovyora-locale', b'').decode('latin1'))
    if chosen:
        return chosen

    path = scope.get('path', '')
    first = path.lstrip('/').split('/', 1)[0]
    chosen = _locale(first)
    if chosen:
        return chosen

    query = parse_qs(scope.get('query_string', b'').decode('latin1'))
    chosen = _locale((query.get('lang') or [''])[0])
    if chosen:
        return chosen

    try:
        cookie = SimpleCookie()
        cookie.load(headers.get(b'cookie', b'').decode('latin1'))
        for key in ('vyora_locale', 'geovyora_admin_locale'):
            chosen = _locale(cookie[key].value if key in cookie else '')
            if chosen:
                return chosen
    except Exception:
        pass

    referer = headers.get(b'referer', b'').decode('latin1')
    chosen = _locale(urlsplit(referer).path.lstrip('/').split('/', 1)[0])
    if chosen:
        return chosen

    for part in headers.get(b'accept-language', b'').decode('latin1').split(','):
        chosen = _locale(part.split(';', 1)[0])
        if chosen:
            return chosen
    return 'fr'


def error_message(detail, status_code, locale):
    """Translate known interface phrases; never expose unknown exception text."""
    translated = localized_message(detail, locale)
    if translated:
        return translated
    messages = ERRORS.get(status_code, ERRORS[500])
    return messages.get(locale, messages['fr'])


def localized_message(value, locale):
    """Translate a known interface or job message; safely hide unknown text."""
    if not isinstance(value, str) or not value:
        return ''
    index = LOCALES.get(locale, 0)
    translations = PHRASES.get(value)
    if translations:
        return translations[index]
    for source, values in PHRASES.items():
        if value in values:
            return values[index]
    return ''


def error_payload(detail, status_code, locale):
    return {'detail': error_message(detail, status_code, locale)}
