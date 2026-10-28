"""Classify network failures without echoing requests, endpoints or secrets."""
import socket,ssl
from urllib.error import URLError


def describe(exc):
    status=getattr(getattr(exc,'response',None),'status_code',None) or getattr(exc,'code',None)
    if isinstance(status,int):
        if status in (401,403):return 'XM-SETUP-AUTH','Anmeldung vom Server abgelehnt. Zugangsdaten und Freischaltung prüfen.'
        if 400<=status<600:return 'XM-SETUP-HTTP','Der Server meldet einen HTTP-Fehler. Später erneut prüfen.'
    cause=exc.reason if isinstance(exc,URLError) else exc
    if isinstance(cause,socket.gaierror):return 'XM-SETUP-DNS','Servername konnte nicht aufgelöst werden. Adresse und Internetverbindung prüfen.'
    if isinstance(cause,ssl.SSLError):return 'XM-SETUP-TLS','Die sichere Verbindung konnte nicht bestätigt werden. Serveradresse, Datum und Zertifikat prüfen.'
    if isinstance(cause,TimeoutError) or type(cause).__name__ in ('ReadTimeout','ConnectTimeout','PoolTimeout','WriteTimeout'):
        return 'XM-SETUP-TIMEOUT','Die einzelne Verbindungsanfrage hat zu lange gedauert. Eingaben bleiben erhalten; erneut prüfen oder später fortsetzen.'
    if isinstance(cause,ConnectionError) or type(cause).__name__ in ('ConnectError','NetworkError'):
        return 'XM-SETUP-NET','Server nicht erreichbar. Verbindung und Serveradresse prüfen.'
    return None
