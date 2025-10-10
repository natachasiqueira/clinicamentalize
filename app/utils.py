"""
Utilitários para manipulação de timezone e datas
"""
from datetime import datetime, timezone
import pytz
from flask import current_app


def get_timezone():
    """
    Retorna o objeto timezone configurado na aplicação
    """
    timezone_name = current_app.config.get('TIMEZONE', 'America/Sao_Paulo')
    return pytz.timezone(timezone_name)


def get_local_now():
    """
    Retorna o datetime atual no timezone configurado da aplicação
    """
    utc_now = datetime.now(timezone.utc)
    local_tz = get_timezone()
    return utc_now.astimezone(local_tz)


def convert_to_local(utc_datetime):
    """
    Converte um datetime UTC para o timezone local configurado
    
    Args:
        utc_datetime: datetime object em UTC (pode ser naive ou aware)
    
    Returns:
        datetime object no timezone local
    """
    if utc_datetime is None:
        return None
    
    # Se o datetime é naive, assume que é UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    
    local_tz = get_timezone()
    return utc_datetime.astimezone(local_tz)


def convert_to_utc(local_datetime):
    """
    Converte um datetime local para UTC
    
    Args:
        local_datetime: datetime object no timezone local (pode ser naive ou aware)
    
    Returns:
        datetime object em UTC
    """
    if local_datetime is None:
        return None
    
    # Se o datetime é naive, assume que é no timezone local
    if local_datetime.tzinfo is None:
        local_tz = get_timezone()
        local_datetime = local_tz.localize(local_datetime)
    
    return local_datetime.astimezone(timezone.utc)


def format_local_datetime(utc_datetime, format_string='%d/%m/%Y %H:%M'):
    """
    Formata um datetime UTC para exibição no timezone local
    
    Args:
        utc_datetime: datetime object em UTC
        format_string: string de formatação (padrão: '%d/%m/%Y %H:%M')
    
    Returns:
        string formatada no timezone local
    """
    if utc_datetime is None:
        return ''
    
    local_dt = convert_to_local(utc_datetime)
    return local_dt.strftime(format_string)


def format_local_time(utc_datetime, format_string='%H:%M'):
    """
    Formata apenas o horário de um datetime UTC para exibição no timezone local
    
    Args:
        utc_datetime: datetime object em UTC
        format_string: string de formatação (padrão: '%H:%M')
    
    Returns:
        string formatada no timezone local
    """
    return format_local_datetime(utc_datetime, format_string)