"""
SimpleDateUtil - Une bibliothèque Python pour la manipulation des dates.
Cette bibliothèque offre des fonctionnalités simples mais complètes pour gérer les dates.
"""

import datetime
import re
import calendar
import math
import os
import time
import struct
from typing import Union, List, Optional, Tuple, Dict, Any, Iterator, Set, Callable

class DateParser:
    """Classe responsable de l'analyse des chaînes de dates."""
    
    # Dictionnaire de mois en français pour la conversion
    _FRENCH_MONTHS = {
        "janvier": 1, "février": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "août": 8, 
        "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
        # Formes abrégées
        "jan": 1, "fév": 2, "mar": 3, "avr": 4,
        "mai": 5, "jun": 6, "jul": 7, "aoû": 8,
        "sep": 9, "oct": 10, "nov": 11, "déc": 12
    }
    
    @staticmethod
    def parse(date_string: str) -> datetime.datetime:
        """
        Analyse une chaîne de caractères contenant une date et la convertit en objet datetime.
        
        Args:
            date_string: Chaîne de caractères représentant une date.
            
        Returns:
            Un objet datetime.
            
        Raises:
            ValueError: Si la chaîne ne peut pas être analysée.
        """
        # Essayer d'abord le format français spécifique "15 avril 2023"
        try:
            return DateParser._parse_french_date(date_string)
        except ValueError:
            pass
            
        # Formats communs à essayer
        formats = [
            "%Y-%m-%d",  # 2023-01-25
            "%d/%m/%Y",  # 25/01/2023
            "%d-%m-%Y",  # 25-01-2023
            "%Y/%m/%d",  # 2023/01/25
            "%d %b %Y",  # 25 Jan 2023
            "%d %B %Y",  # 25 January 2023
            "%B %d, %Y",  # January 25, 2023
            "%Y-%m-%dT%H:%M:%S",  # ISO format 2023-01-25T14:30:00
            "%Y-%m-%d %H:%M:%S",  # 2023-01-25 14:30:00
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_string, fmt)
            except ValueError:
                continue
                
        # Essayer de détecter des formats relatifs comme "aujourd'hui", "demain", etc.
        relative_date = DateParser._parse_relative_date(date_string)
        if relative_date:
            return relative_date
            
        raise ValueError(f"Format de date non reconnu: {date_string}")
    
    @staticmethod
    def _parse_french_date(date_string: str) -> datetime.datetime:
        """
        Analyse les dates en format français comme "15 avril 2023"
        
        Args:
            date_string: Date au format "jour mois année"
            
        Returns:
            datetime.datetime: Date analysée
            
        Raises:
            ValueError: Si la date ne peut pas être analysée
        """
        date_string = date_string.lower().strip()
        
        # Format: "15 avril 2023"
        match = re.match(r"(\d{1,2})\s+([a-zéûôù]+)\s+(\d{4})", date_string)
        if match:
            day, month_name, year = match.groups()
            
            # Convertir le nom du mois en numéro
            if month_name in DateParser._FRENCH_MONTHS:
                month = DateParser._FRENCH_MONTHS[month_name]
                return datetime.datetime(int(year), month, int(day))
        
        raise ValueError(f"Format de date français non reconnu: {date_string}")
    
    @staticmethod
    def _parse_relative_date(date_string: str) -> Optional[datetime.datetime]:
        """Analyse les dates relatives comme "aujourd'hui", "demain", etc."""
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_string = date_string.lower().strip()
        
        if date_string in ["aujourd'hui", "today"]:
            return today
        elif date_string in ["demain", "tomorrow"]:
            return today + datetime.timedelta(days=1)
        elif date_string in ["hier", "yesterday"]:
            return today - datetime.timedelta(days=1)
        
        # Recherche de modèles comme "dans 3 jours" ou "il y a 2 semaines"
        future_match = re.match(r"dans (\d+) (jour|jours|semaine|semaines|mois|an|ans)", date_string)
        past_match = re.match(r"il y a (\d+) (jour|jours|semaine|semaines|mois|an|ans)", date_string)
        
        if future_match:
            value, unit = int(future_match.group(1)), future_match.group(2)
            return DateParser._adjust_date(today, value, unit)
        elif past_match:
            value, unit = int(past_match.group(1)), past_match.group(2)
            return DateParser._adjust_date(today, -value, unit)
            
        return None
    
    @staticmethod
    def _adjust_date(base_date: datetime.datetime, value: int, unit: str) -> datetime.datetime:
        """Ajuste une date en fonction d'une valeur et d'une unité de temps."""
        if unit in ["jour", "jours"]:
            return base_date + datetime.timedelta(days=value)
        elif unit in ["semaine", "semaines"]:
            return base_date + datetime.timedelta(weeks=value)
        elif unit in ["mois"]:
            # Ajuster le mois en tenant compte du changement d'année si nécessaire
            new_month = base_date.month + value
            new_year = base_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            
            # Gérer les problèmes comme le 31 janvier + 1 mois (qui n'existe pas)
            day = min(base_date.day, calendar.monthrange(new_year, new_month)[1])
            
            return base_date.replace(year=new_year, month=new_month, day=day)
        elif unit in ["an", "ans"]:
            return base_date.replace(year=base_date.year + value)
        
        return base_date


class DateFormatter:
    """Classe responsable du formatage des dates."""
    
    @staticmethod
    def format(date: datetime.datetime, format_string: str = "%Y-%m-%d") -> str:
        """
        Formate une date selon un modèle spécifié.
        
        Args:
            date: Date à formater.
            format_string: Chaîne de format (par défaut ISO).
            
        Returns:
            Chaîne de date formatée.
        """
        return date.strftime(format_string)
    
    @staticmethod
    def to_iso(date: datetime.datetime) -> str:
        """Convertit une date au format ISO 8601."""
        return date.isoformat()
    
    @staticmethod
    def to_human_readable(date: datetime.datetime, locale: str = "fr") -> str:
        """
        Retourne une représentation lisible par un humain de la date.
        
        Args:
            date: Date à formater.
            locale: Langue à utiliser (fr ou en).
            
        Returns:
            Chaîne de date formatée.
        """
        if locale == "fr":
            months = ["janvier", "février", "mars", "avril", "mai", "juin", 
                     "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
            return f"{date.day} {months[date.month - 1]} {date.year}"
        else:  # default to English
            return date.strftime("%B %d, %Y")

class DateCalculator:
    """Classe responsable des calculs sur les dates."""
    
    @staticmethod
    def add_days(date: datetime.datetime, days: int) -> datetime.datetime:
        """Ajoute un nombre de jours à une date."""
        return date + datetime.timedelta(days=days)
    
    @staticmethod
    def add_months(date: datetime.datetime, months: int) -> datetime.datetime:
        """Ajoute un nombre de mois à une date."""
        new_month = date.month + months
        new_year = date.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        
        # Gérer les cas comme le 31 janvier + 1 mois
        day = min(date.day, calendar.monthrange(new_year, new_month)[1])
        
        return date.replace(year=new_year, month=new_month, day=day)
    
    @staticmethod
    def add_years(date: datetime.datetime, years: int) -> datetime.datetime:
        """Ajoute un nombre d'années à une date."""
        new_year = date.year + years
        
        # Gérer le 29 février pour les années non bissextiles
        if date.month == 2 and date.day == 29 and not calendar.isleap(new_year):
            return date.replace(year=new_year, day=28)
        
        return date.replace(year=new_year)
    
    @staticmethod
    def difference_in_days(date1: datetime.datetime, date2: datetime.datetime) -> int:
        """Calcule la différence en jours entre deux dates."""
        return (date2 - date1).days
    
    @staticmethod
    def difference_in_months(date1: datetime.datetime, date2: datetime.datetime) -> int:
        """Calcule la différence approximative en mois entre deux dates."""
        return (date2.year - date1.year) * 12 + date2.month - date1.month
    
    @staticmethod
    def is_between(date: datetime.datetime, start: datetime.datetime, end: datetime.datetime) -> bool:
        """Vérifie si une date est entre deux autres dates."""
        return start <= date <= end


class DateRange:
    """Classe représentant une plage de dates."""
    
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        """
        Initialise une plage de dates.
        
        Args:
            start: Date de début.
            end: Date de fin.
            
        Raises:
            ValueError: Si la date de fin est antérieure à la date de début.
        """
        if end < start:
            raise ValueError("La date de fin doit être postérieure ou égale à la date de début")
        
        self.start = start
        self.end = end
    
    def contains(self, date: datetime.datetime) -> bool:
        """Vérifie si une date est dans la plage."""
        return self.start <= date <= self.end
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Vérifie si cette plage chevauche une autre plage."""
        return self.start <= other.end and other.start <= self.end
    
    def get_days(self) -> List[datetime.datetime]:
        """Retourne une liste de toutes les dates dans la plage."""
        days = []
        current = self.start
        
        while current <= self.end:
            days.append(current)
            current += datetime.timedelta(days=1)
        
        return days
    
    def __iter__(self):
        """Permet d'itérer sur les jours de la plage."""
        self._current = self.start
        return self
    
    def __next__(self):
        """Retourne le jour suivant lors de l'itération."""
        if self._current > self.end:
            raise StopIteration
        
        current = self._current
        self._current += datetime.timedelta(days=1)
        return current
    
    def __len__(self):
        """Retourne le nombre de jours dans la plage."""
        return (self.end - self.start).days + 1


class DateValidator:
    """Classe pour valider les dates."""
    
    @staticmethod
    def is_valid_date(year: int, month: int, day: int) -> bool:
        """Vérifie si une date est valide."""
        try:
            datetime.date(year, month, day)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_future_date(date: datetime.datetime) -> bool:
        """Vérifie si une date est dans le futur."""
        return date > datetime.datetime.now()
    
    @staticmethod
    def is_past_date(date: datetime.datetime) -> bool:
        """Vérifie si une date est dans le passé."""
        return date < datetime.datetime.now()
    
    @staticmethod
    def is_weekend(date: datetime.datetime) -> bool:
        """Vérifie si une date tombe un week-end (samedi ou dimanche)."""
        return date.weekday() >= 5  # 5 = samedi, 6 = dimanche
    
    @staticmethod
    def is_weekday(date: datetime.datetime) -> bool:
        """Vérifie si une date tombe un jour de semaine."""
        return date.weekday() < 5


class BusinessDays:
    """Classe pour travailler avec les jours ouvrables."""
    
    def __init__(self, holidays: Optional[List[datetime.date]] = None):
        """
        Initialise un calculateur de jours ouvrables.
        
        Args:
            holidays: Liste optionnelle de jours fériés à exclure.
        """
        self.holidays = holidays or []
    
    def is_business_day(self, date: datetime.datetime) -> bool:
        """Vérifie si une date est un jour ouvrable."""
        # Convertir en date si c'est un datetime
        date_only = date.date() if isinstance(date, datetime.datetime) else date
        
        # Pas un jour ouvrable si c'est le week-end ou un jour férié
        return not (date.weekday() >= 5 or date_only in self.holidays)
    
    def add_business_days(self, date: datetime.datetime, days: int) -> datetime.datetime:
        """Ajoute un nombre de jours ouvrables à une date."""
        result = date
        days_added = 0
        
        while days_added < days:
            result += datetime.timedelta(days=1)
            if self.is_business_day(result):
                days_added += 1
                
        return result
    
    def get_business_days_between(self, start: datetime.datetime, end: datetime.datetime) -> int:
        """Calcule le nombre de jours ouvrables entre deux dates."""
        business_days = 0
        current = start
        
        while current <= end:
            if self.is_business_day(current):
                business_days += 1
            current += datetime.timedelta(days=1)
            
        return business_days


class RelativeDelta:
    """
    Classe similaire à timedelta mais avec des capacités plus avancées.
    Permet de représenter des notions comme "ajouter 1 mois" ou "le prochain vendredi".
    """
    
    def __init__(self, dt1=None, dt2=None, years=0, months=0, days=0, 
                 hours=0, minutes=0, seconds=0, microseconds=0,
                 year=None, month=None, day=None, weekday=None,
                 hour=None, minute=None, second=None, microsecond=None):
        """
        Initialise un delta relatif.
        
        Args:
            dt1, dt2: Si spécifiés, calcule le delta entre les deux dates
            years, months, etc.: Valeurs à ajouter/soustraire
            year, month, etc.: Valeurs absolues à définir
            weekday: Peut être un entier (0-6 pour lundi-dimanche) ou un tuple
                     (jour de la semaine, n) où n indique la nième occurrence,
                     comme (FR, 1) pour le premier vendredi
        """
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.microseconds = microseconds
        
        # Valeurs absolues
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        
        # Calculer le delta entre deux dates si spécifiées
        if dt1 and dt2:
            # Convertir en datetime si ce sont des dates
            if isinstance(dt1, datetime.date) and not isinstance(dt1, datetime.datetime):
                dt1 = datetime.datetime.combine(dt1, datetime.time())
            if isinstance(dt2, datetime.date) and not isinstance(dt2, datetime.datetime):
                dt2 = datetime.datetime.combine(dt2, datetime.time())
                
            # Extraire les années et mois
            years = dt2.year - dt1.year
            months = dt2.month - dt1.month
            
            if months < 0:
                years -= 1
                months += 12
                
            # Jour de comparaison pour déterminer les jours restants
            try:
                # Calculer la nouvelle date après avoir ajouté les années et mois
                if months:
                    month = dt1.month + months
                    new_year = dt1.year + years + (month - 1) // 12
                    new_month = ((month - 1) % 12) + 1
                    cmpday = dt1.replace(year=new_year, month=new_month)
                else:
                    cmpday = dt1.replace(year=dt1.year + years)
                
                # Calculer différence en jours, heures, etc.
                days = (dt2 - cmpday).days
                hours = dt2.hour - dt1.hour
                minutes = dt2.minute - dt1.minute
                seconds = dt2.second - dt1.second
                microseconds = dt2.microsecond - dt1.microsecond
                
                # Normaliser
                if microseconds < 0:
                    seconds -= 1
                    microseconds += 1000000
                if seconds < 0:
                    minutes -= 1
                    seconds += 60
                if minutes < 0:
                    hours -= 1
                    minutes += 60
                if hours < 0:
                    days -= 1
                    hours += 24
                    
                self.years = years
                self.months = months
                self.days = days
                self.hours = hours
                self.minutes = minutes
                self.seconds = seconds
                self.microseconds = microseconds
            except ValueError:
                # Si la date de comparaison ne peut pas être créée (comme 30 février)
                # Utiliser une approche plus simple
                delta = dt2 - dt1
                self.days = delta.days
                self.seconds = delta.seconds
                self.microseconds = delta.microseconds
    
    def __add__(self, other):
        """Permet d'ajouter ce delta à une date ou à un autre delta."""
        if isinstance(other, datetime.datetime):
            return self._add_to_datetime(other)
        elif isinstance(other, datetime.date):
            return self._add_to_date(other)
        elif isinstance(other, RelativeDelta):
            return self._add_to_relativedelta(other)
        return NotImplemented
    
    def _add_to_datetime(self, dt):
        """Ajoute ce delta à un objet datetime."""
        # Ajouter années et mois
        year = dt.year + self.years
        month = dt.month + self.months
        
        if month > 12:
            year += month // 12
            month = month % 12
            if month == 0:
                month = 12
                year -= 1
            
        # Déterminer le jour maximum du mois
        day = min(dt.day, calendar.monthrange(year, month)[1])
        
        # Appliquer les valeurs absolues si définies
        if self.year is not None:
            year = self.year
        if self.month is not None:
            month = self.month
        if self.day is not None:
            day = self.day
        
        # Créer une nouvelle date avec les années/mois/jours mis à jour
        result = dt.replace(year=year, month=month, day=day)
        
        # Ajouter les jours, heures, etc.
        delta = datetime.timedelta(days=self.days, hours=self.hours, 
                                   minutes=self.minutes, seconds=self.seconds,
                                   microseconds=self.microseconds)
        result += delta
        
        # Appliquer les autres valeurs absolues
        if self.hour is not None:
            result = result.replace(hour=self.hour)
        if self.minute is not None:
            result = result.replace(minute=self.minute)
        if self.second is not None:
            result = result.replace(second=self.second)
        if self.microsecond is not None:
            result = result.replace(microsecond=self.microsecond)
        
        # Gérer weekday (jour de la semaine)
        if self.weekday is not None:
            if isinstance(self.weekday, tuple):
                weekday, n = self.weekday
                # Calculer le nième jour de la semaine du mois
                # weekday est 0-6 (lundi-dimanche)
                day_of_week = weekday  # 0-6 pour lundi-dimanche
                
                # Trouver le premier jour du mois
                first_day = result.replace(day=1)
                
                # Calculer le jour du mois du premier jour de la semaine demandé
                first_matching_day = 1 + (day_of_week - first_day.weekday()) % 7
                
                # Calculer le jour du mois du nième jour de la semaine
                target_day = first_matching_day + (n - 1) * 7
                
                # Si n est négatif, compter à partir de la fin du mois
                if n < 0:
                    days_in_month = calendar.monthrange(result.year, result.month)[1]
                    last_matching_day = first_matching_day
                    while last_matching_day + 7 <= days_in_month:
                        last_matching_day += 7
                    target_day = last_matching_day + (n + 1) * 7
                
                if 1 <= target_day <= calendar.monthrange(result.year, result.month)[1]:
                    result = result.replace(day=target_day)
            else:
                # Avancer au prochain jour de la semaine spécifié
                days_ahead = (self.weekday - result.weekday()) % 7
                if days_ahead:
                    result += datetime.timedelta(days=days_ahead)
        
        return result
    
    def _add_to_date(self, dt):
        """Ajoute ce delta à un objet date."""
        # Convertir en datetime puis appliquer le delta
        dt_datetime = datetime.datetime.combine(dt, datetime.time())
        result_datetime = self._add_to_datetime(dt_datetime)
        return result_datetime.date()
    
    def _add_to_relativedelta(self, other):
        """Combine deux RelativeDelta."""
        return RelativeDelta(
            years=self.years + other.years,
            months=self.months + other.months,
            days=self.days + other.days,
            hours=self.hours + other.hours,
            minutes=self.minutes + other.minutes,
            seconds=self.seconds + other.seconds,
            microseconds=self.microseconds + other.microseconds,
            year=other.year if other.year is not None else self.year,
            month=other.month if other.month is not None else self.month,
            day=other.day if other.day is not None else self.day,
            weekday=other.weekday if other.weekday is not None else self.weekday,
            hour=other.hour if other.hour is not None else self.hour,
            minute=other.minute if other.minute is not None else self.minute,
            second=other.second if other.second is not None else self.second,
            microsecond=other.microsecond if other.microsecond is not None else self.microsecond
        )
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __rsub__(self, other):
        neg = self.__neg__()
        return neg.__add__(other)
    
    def __neg__(self):
        return RelativeDelta(
            years=-self.years,
            months=-self.months,
            days=-self.days,
            hours=-self.hours,
            minutes=-self.minutes,
            seconds=-self.seconds,
            microseconds=-self.microseconds,
            year=self.year,
            month=self.month,
            day=self.day,
            weekday=self.weekday,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond
        )
    
    def __str__(self):
        """
        Retourne une représentation en chaîne du delta relatif.
        Simplifie l'affichage pour montrer la plus grande unité de temps possible.
        """
        # Convertir en mois totaux
        total_months = self.years * 12 + self.months
        
        # Si nous n'avons que des mois (et potentiellement des années), simplifier à "months=X"
        if total_months != 0 and self.days == 0 and self.hours == 0 and self.minutes == 0 and \
           self.seconds == 0 and self.microseconds == 0:
            return f"relativedelta(months={'+' if total_months > 0 else ''}{total_months})"
        
        # Si nous avons seulement des jours, simplifier à "days=X"
        if self.years == 0 and self.months == 0 and self.days != 0 and self.hours == 0 and \
           self.minutes == 0 and self.seconds == 0 and self.microseconds == 0:
            return f"relativedelta(days={'+' if self.days > 0 else ''}{self.days})"
        
        # Affichage standard pour les cas plus complexes
        attrs = []
        if self.years:
            attrs.append(f"years={'+' if self.years > 0 else ''}{self.years}")
        if self.months:
            attrs.append(f"months={'+' if self.months > 0 else ''}{self.months}")
        if self.days:
            attrs.append(f"days={'+' if self.days > 0 else ''}{self.days}")
        if self.hours:
            attrs.append(f"hours={'+' if self.hours > 0 else ''}{self.hours}")
        if self.minutes:
            attrs.append(f"minutes={'+' if self.minutes > 0 else ''}{self.minutes}")
        if self.seconds:
            attrs.append(f"seconds={'+' if self.seconds > 0 else ''}{self.seconds}")
        if self.microseconds:
            attrs.append(f"microseconds={'+' if self.microseconds > 0 else ''}{self.microseconds}")
        
        if not attrs:
            return "relativedelta()"
        
        return "relativedelta({})".format(", ".join(attrs))

# Constantes pour les jours de la semaine
MO, TU, WE, TH, FR, SA, SU = range(7)

class Recurrence:
    """
    Classe pour générer des récurrences selon des règles flexibles.
    Similaire à rrule de dateutil.
    """
    
    # Constantes pour les fréquences
    YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY = range(7)
    
    def __init__(self, freq, dtstart=None, interval=1, wkst=MO,
                 count=None, until=None, bymonth=None, bymonthday=None,
                 byyearday=None, byweekno=None, byweekday=None, bysetpos=None,
                 byhour=None, byminute=None, bysecond=None):
        """
        Initialise une règle de récurrence.
        
        Args:
            freq: Fréquence (YEARLY, MONTHLY, etc.)
            dtstart: Date de début
            interval: Intervalle entre les occurrences
            wkst: Premier jour de la semaine (MO, TU, etc.)
            count: Nombre maximal d'occurrences
            until: Date limite pour les occurrences
            bymonth, bymonthday, etc.: Filtres pour les occurrences
            bysetpos: Position dans l'ensemble des occurrences (ex: 1 pour premier, -1 pour dernier)
        """
        self.freq = freq
        self.dtstart = dtstart or datetime.datetime.now()
        self.interval = interval
        self.wkst = wkst
        self.count = count
        self.until = until
        
        # Filtres
        self.bymonth = bymonth
        self.bymonthday = bymonthday
        self.byyearday = byyearday
        self.byweekno = byweekno
        self.byweekday = byweekday
        self.bysetpos = bysetpos
        self.byhour = byhour
        self.byminute = byminute
        self.bysecond = bysecond
        
        # Convertir les filtres en listes si ce sont des entiers
        self._normalize_filter('bymonth')
        self._normalize_filter('bymonthday')
        self._normalize_filter('byyearday')
        self._normalize_filter('byweekno')
        self._normalize_filter('byweekday')
        self._normalize_filter('bysetpos')
        self._normalize_filter('byhour')
        self._normalize_filter('byminute')
        self._normalize_filter('bysecond')
    
    def _normalize_filter(self, attr):
        """Convertit un filtre en liste s'il s'agit d'un entier ou None."""
        value = getattr(self, attr)
        if value is None:
            setattr(self, attr, [])
        elif isinstance(value, int):
            setattr(self, attr, [value])
    
    def __iter__(self):
        """Permet d'itérer sur les occurrences."""
        return self._iter()
    
    def _iter(self):
        """Générateur pour les occurrences."""
        count = 0
        current = self.dtstart
        
        while True:
            # Vérifier les limites
            if self.count is not None and count >= self.count:
                break
            if self.until is not None and current > self.until:
                break
            
            # Générer les occurrences pour la période actuelle
            occurrences = self._get_period_occurrences(current)
            
            # Appliquer bysetpos si nécessaire
            if self.bysetpos:
                # Trier les positions demandées
                positions = sorted(self.bysetpos)
                
                # Calculer les occurrences aux positions demandées
                selected_occurrences = []
                for pos in positions:
                    if pos > 0 and pos <= len(occurrences):
                        selected_occurrences.append(occurrences[pos - 1])
                    elif pos < 0 and abs(pos) <= len(occurrences):
                        selected_occurrences.append(occurrences[pos])
                
                occurrences = sorted(selected_occurrences)
            
            # Retourner les occurrences
            for dt in occurrences:
                if self.until is not None and dt > self.until:
                    return
                
                yield dt
                count += 1
                
                if self.count is not None and count >= self.count:
                    return
            
            # Passer à la période suivante
            current = self._next_period(current)
    
    def _next_period(self, dt):
        """Calcule le début de la période suivante."""
        if self.freq == self.YEARLY:
            return dt.replace(year=dt.year + self.interval)
        elif self.freq == self.MONTHLY:
            year = dt.year + (dt.month + self.interval - 1) // 12
            month = ((dt.month + self.interval - 1) % 12) + 1
            day = min(dt.day, calendar.monthrange(year, month)[1])
            return dt.replace(year=year, month=month, day=day)
        elif self.freq == self.WEEKLY:
            return dt + datetime.timedelta(days=7 * self.interval)
        elif self.freq == self.DAILY:
            return dt + datetime.timedelta(days=self.interval)
        elif self.freq == self.HOURLY:
            return dt + datetime.timedelta(hours=self.interval)
        elif self.freq == self.MINUTELY:
            return dt + datetime.timedelta(minutes=self.interval)
        elif self.freq == self.SECONDLY:
            return dt + datetime.timedelta(seconds=self.interval)
        
        return dt
    
    def _get_period_occurrences(self, dt):
        """Génère toutes les occurrences pour la période actuelle."""
        if self.freq == self.YEARLY:
            # Pour une fréquence annuelle, on doit explorer tous les jours de l'année
            occurrences = []
            year = dt.year
            
            # Si bymonth est spécifié, on ne considère que ces mois
            months = self.bymonth if self.bymonth else range(1, 13)
            
            for month in months:
                days_in_month = calendar.monthrange(year, month)[1]
                for day in range(1, days_in_month + 1):
                    candidate = datetime.datetime(year, month, day)
                    if self._matches_filters(candidate):
                        occurrences.append(candidate)
            
            return occurrences
            
        elif self.freq == self.MONTHLY:
            # Pour une fréquence mensuelle, on doit explorer tous les jours du mois
            occurrences = []
            year, month = dt.year, dt.month
            days_in_month = calendar.monthrange(year, month)[1]
            
            for day in range(1, days_in_month + 1):
                candidate = datetime.datetime(year, month, day)
                if self._matches_filters(candidate):
                    occurrences.append(candidate)
            
            return occurrences
            
        elif self.freq == self.WEEKLY:
            # Pour une fréquence hebdomadaire, on doit explorer tous les jours de la semaine
            occurrences = []
            for i in range(7):
                day = dt + datetime.timedelta(days=i)
                if self._matches_filters(day):
                    occurrences.append(day)
            
            return occurrences
            
        elif self.freq in [self.DAILY, self.HOURLY, self.MINUTELY, self.SECONDLY]:
            # Pour les fréquences plus petites, on vérifie simplement si la date actuelle correspond
            if self._matches_filters(dt):
                return [dt]
            else:
                return []
        
        return []
    
    def _matches_filters(self, dt):
        """Vérifie si une date correspond à tous les filtres."""
        # Filtre par mois
        if self.bymonth and dt.month not in self.bymonth:
            return False
        
        # Filtre par jour du mois
        if self.bymonthday and dt.day not in self.bymonthday:
            return False
        
        # Filtre par jour de l'année
        if self.byyearday:
            day_of_year = dt.timetuple().tm_yday
            if day_of_year not in self.byyearday:
                return False
        
        # Filtre par semaine de l'année
        if self.byweekno:
            week_of_year = int(dt.strftime("%W"))
            if week_of_year not in self.byweekno:
                return False
        
        # Filtre par jour de la semaine
        if self.byweekday:
            weekday = dt.weekday()
            if weekday not in self.byweekday:
                return False
        
        # Filtres pour l'heure, minute, seconde
        if self.byhour and dt.hour not in self.byhour:
            return False
        if self.byminute and dt.minute not in self.byminute:
            return False
        if self.bysecond and dt.second not in self.bysecond:
            return False
        
        return True
    
    def __getitem__(self, item):
        """Permet d'accéder à une occurrence spécifique."""
        import itertools
        
        if isinstance(item, slice):
            return list(itertools.islice(self._iter(), 
                                        item.start, item.stop, item.step))
        else:
            return next(itertools.islice(self._iter(), item, item + 1), None)

class Easter:
    """Classe pour calculer la date de Pâques."""
    
    # Algorithmes pour le calcul de Pâques
    EASTER_WESTERN = 1  # Pâques occidental (grégorien)
    EASTER_ORTHODOX = 2  # Pâques orthodoxe
    EASTER_JULIAN = 3    # Pâques julien
    
    @staticmethod
    def easter(year, method=EASTER_WESTERN):
        """
        Calcule la date de Pâques pour une année donnée.
        
        Args:
            year: Année
            method: Méthode de calcul (EASTER_WESTERN, EASTER_ORTHODOX, EASTER_JULIAN)
            
        Returns:
            datetime.date: Date de Pâques
        """
        if method == Easter.EASTER_WESTERN:
            return Easter._easter_western(year)
        elif method == Easter.EASTER_ORTHODOX:
            return Easter._easter_orthodox(year)
        elif method == Easter.EASTER_JULIAN:
            return Easter._easter_julian(year)
        else:
            raise ValueError("Méthode de calcul de Pâques non reconnue")
    
    @staticmethod
    def _easter_western(year):
        """Calcule la date de Pâques selon la méthode occidentale (grégorienne)."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return datetime.date(year, month, day)
    
    @staticmethod
    def _easter_orthodox(year):
        """Calcule la date de Pâques selon la méthode orthodoxe."""
        # D'abord calculer la date selon le calendrier julien
        julian_easter = Easter._easter_julian(year)
        
        # Puis convertir en date grégorienne
        # Le décalage entre les calendriers julien et grégorien dépend de l'année
        if year < 1900:
            delta = 12 if year >= 1800 else 11
        elif year < 2100:
            delta = 13
        else:
            delta = 14  # pour les années 2100-2199
        
        return julian_easter + datetime.timedelta(days=delta)
    
    @staticmethod
    def _easter_julian(year):
        """Calcule la date de Pâques selon le calendrier julien."""
        a = year % 4
        b = year % 7
        c = year % 19
        d = (19 * c + 15) % 30
        e = (2 * a + 4 * b - d + 34) % 7
        month = (d + e + 114) // 31
        day = ((d + e + 114) % 31) + 1
        
        # Le résultat est dans le calendrier julien
        # Convertir en date grégorienne pour la cohérence
        julian_day = day
        julian_month = month
        julian_year = year
        
        return datetime.date(julian_year, julian_month, julian_day)


class TimeZone:
    """Classe pour gérer les fuseaux horaires."""
    
    @staticmethod
    def get_timezone(tz_name):
        """
        Retourne un objet tzinfo pour le fuseau horaire spécifié.
        
        Args:
            tz_name: Nom du fuseau horaire ou chemin vers un fichier tzfile
            
        Returns:
            datetime.tzinfo: Objet tzinfo
        """
        # Pour simplifier, on utilise les fonctionnalités de base de datetime
        # Une implémentation complète utiliserait des bibliothèques comme pytz
        # ou gérerait directement les fichiers de zone.
        if tz_name.upper() == "UTC":
            return TimeZone.utc()
        else:
            raise ValueError(f"Fuseau horaire non pris en charge: {tz_name}")
    
    @staticmethod
    def utc():
        """Retourne l'objet tzinfo pour UTC."""
        return datetime.timezone.utc
    
    @staticmethod
    def local():
        """Retourne l'objet tzinfo pour le fuseau horaire local."""
        # Cette implémentation simplifiée ne prend pas en compte les changements d'heure
        utc_offset = -time.timezone
        return datetime.timezone(datetime.timedelta(seconds=utc_offset))
    
    @staticmethod
    def fixed_offset(offset_hours):
        """
        Crée un fuseau horaire avec un décalage fixe par rapport à UTC.
        
        Args:
            offset_hours: Décalage en heures (peut être un nombre décimal)
            
        Returns:
            datetime.tzinfo: Objet tzinfo
        """
        offset_seconds = int(offset_hours * 3600)
        return datetime.timezone(datetime.timedelta(seconds=offset_seconds))


class DateUtils:
    """Façade principale pour la bibliothèque."""
    
    @staticmethod
    def parse(date_string: str) -> datetime.datetime:
        """Analyse une chaîne de date."""
        return DateParser.parse(date_string)
    
    @staticmethod
    def format(date: datetime.datetime, format_string: str = "%Y-%m-%d") -> str:
        """Formate une date."""
        return DateFormatter.format(date, format_string)
    
    @staticmethod
    def add_days(date: datetime.datetime, days: int) -> datetime.datetime:
        """Ajoute des jours à une date."""
        return DateCalculator.add_days(date, days)
    
    @staticmethod
    def add_months(date: datetime.datetime, months: int) -> datetime.datetime:
        """Ajoute des mois à une date."""
        return DateCalculator.add_months(date, months)
    
    @staticmethod
    def add_years(date: datetime.datetime, years: int) -> datetime.datetime:
        """Ajoute des années à une date."""
        return DateCalculator.add_years(date, years)
    
    @staticmethod
    def create_range(start: datetime.datetime, end: datetime.datetime) -> DateRange:
        """Crée une plage de dates."""
        return DateRange(start, end)
    
    @staticmethod
    def is_valid_date(year: int, month: int, day: int) -> bool:
        """Vérifie si une date est valide."""
        return DateValidator.is_valid_date(year, month, day)
    
    @staticmethod
    def is_weekend(date: datetime.datetime) -> bool:
        """Vérifie si une date tombe un week-end."""
        return DateValidator.is_weekend(date)
    
    @staticmethod
    def business_calculator(holidays: Optional[List[datetime.date]] = None) -> BusinessDays:
        """Crée un calculateur de jours ouvrables."""
        return BusinessDays(holidays)
    
    @staticmethod
    def now() -> datetime.datetime:
        """Retourne la date et l'heure actuelles."""
        return datetime.datetime.now()
    
    @staticmethod
    def today() -> datetime.datetime:
        """Retourne la date actuelle à minuit."""
        now = datetime.datetime.now()
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def relativedelta(**kwargs) -> RelativeDelta:
        """Crée un delta relatif."""
        return RelativeDelta(**kwargs)
    
    @staticmethod
    def rrule(freq, **kwargs) -> Recurrence:
        """Crée une règle de récurrence."""
        return Recurrence(freq, **kwargs)
    
    @staticmethod
    def easter(year: int, method: int = Easter.EASTER_WESTERN) -> datetime.date:
        """Calcule la date de Pâques pour une année donnée."""
        return Easter.easter(year, method)
    
    @staticmethod
    def get_timezone(tz_name: str) -> datetime.tzinfo:
        """Retourne un fuseau horaire."""
        return TimeZone.get_timezone(tz_name)
    
    @staticmethod
    def utc() -> datetime.tzinfo:
        """Retourne le fuseau horaire UTC."""
        return TimeZone.utc()
    
    @staticmethod
    def local_timezone() -> datetime.tzinfo:
        """Retourne le fuseau horaire local."""
        return TimeZone.local()

def samples():
    print("\n=== EXEMPLES D'UTILISATION DE SIMPLEDATEUTIL ===\n")
    
    # 1. Analyse et formatage de dates
    print("1. Analyse et formatage de dates:")
    date1 = DateUtils.parse("2023-04-15")
    date2 = DateUtils.parse("15/04/2023")
    date3 = DateUtils.parse("15 avril 2023")
    print(f"Date analysée 1: {date1}")
    print(f"Date analysée 2: {date2}")
    print(f"Date analysée 3: {date3}")
    
    # Formatage
    formatted1 = DateUtils.format(date1, "%d %B %Y")
    formatted2 = DateUtils.format(date1, "%A, %d %B %Y")
    formatted3 = DateUtils.format(date1, "%Y-%m-%d %H:%M:%S")
    print(f"Date formatée 1: {formatted1}")
    print(f"Date formatée 2: {formatted2}")
    print(f"Date formatée 3: {formatted3}")
    
    # 2. Calculs de dates simples
    print("\n2. Calculs de dates simples:")
    today = DateUtils.today()
    print(f"Aujourd'hui: {today}")
    
    tomorrow = DateUtils.add_days(today, 1)
    print(f"Demain: {tomorrow}")
    
    next_month = DateUtils.add_months(today, 1)
    print(f"Mois prochain: {next_month}")
    
    next_year = DateUtils.add_years(today, 1)
    print(f"Année prochaine: {next_year}")
    
    # 3. Plages de dates
    print("\n3. Plages de dates:")
    start_date = DateUtils.parse("2023-04-01")
    end_date = DateUtils.parse("2023-04-10")
    date_range = DateUtils.create_range(start_date, end_date)
    
    print(f"Plage du {start_date.date()} au {end_date.date()}: {len(date_range)} jours")
    print("Dates dans la plage:")
    for day in date_range:
        print(f"  - {day.date()}")
    
    # 4. Validation de dates
    print("\n4. Validation de dates:")
    valid_date = DateUtils.is_valid_date(2023, 4, 15)
    invalid_date = DateUtils.is_valid_date(2023, 2, 30)
    print(f"2023-04-15 est valide: {valid_date}")
    print(f"2023-02-30 est valide: {invalid_date}")
    
    weekend = DateUtils.is_weekend(DateUtils.parse("2023-04-15"))  # Un samedi
    print(f"2023-04-15 est un weekend: {weekend}")
    
    # 5. Jours ouvrables
    print("\n5. Jours ouvrables:")
    holidays = [
        datetime.date(2023, 4, 7),  # Vendredi Saint
        datetime.date(2023, 4, 10)  # Lundi de Pâques
    ]
    business_calc = DateUtils.business_calculator(holidays)
    
    business_start = DateUtils.parse("2023-04-03")  # Lundi
    business_end = DateUtils.parse("2023-04-14")    # Vendredi (semaine suivante)
    
    business_days = business_calc.get_business_days_between(business_start, business_end)
    print(f"Jours ouvrables entre le 03/04/2023 et le 14/04/2023: {business_days}")
    
    next_business_day = business_calc.add_business_days(business_start, 5)
    print(f"5 jours ouvrables après le 03/04/2023: {next_business_day.date()}")
    
    # 6. Calcul de Pâques
    print("\n6. Calcul de Pâques:")
    easter_2023 = DateUtils.easter(2023)
    easter_2024 = DateUtils.easter(2024)
    easter_2025 = DateUtils.easter(2025)
    print(f"Pâques 2023: {easter_2023}")
    print(f"Pâques 2024: {easter_2024}")
    print(f"Pâques 2025: {easter_2025}")
    
    orthodox_easter = DateUtils.easter(2023, Easter.EASTER_ORTHODOX)
    print(f"Pâques orthodoxe 2023: {orthodox_easter}")
    
    # 7. RelativeDelta - deltas relatifs
    print("\n7. RelativeDelta - deltas relatifs:")
    now = DateUtils.now()
    
    # Ajouter 1 mois et 5 jours
    delta1 = DateUtils.relativedelta(months=1, days=5)
    future_date = now + delta1
    print(f"Aujourd'hui + 1 mois et 5 jours: {future_date}")
    
    # Prochain vendredi
    next_friday = now + DateUtils.relativedelta(weekday=FR)
    print(f"Prochain vendredi: {next_friday}")
    
    # Dernier jour du mois
    last_day = now + DateUtils.relativedelta(day=31)
    print(f"Dernier jour du mois (ou max possible): {last_day}")
    
    # Premier jour du mois prochain
    first_next_month = now + DateUtils.relativedelta(day=1, months=1)
    print(f"Premier jour du mois prochain: {first_next_month}")
    
    # Différence entre deux dates
    date_1 = DateUtils.parse("2020-01-01")
    date_2 = DateUtils.parse("2023-06-15")
    diff = RelativeDelta(date_1, date_2)
    print(f"Différence entre 2020-01-01 et 2023-06-15: {diff}")
    
    # 8. Récurrences
    print("\n8. Récurrences:")
    
    # Tous les premiers lundis du mois pour l'année
    start = DateUtils.parse("2023-01-01")
    r = DateUtils.rrule(
        Recurrence.MONTHLY,
        dtstart=start,
        count=12,
        byweekday=MO,
        bysetpos=1  # Premier lundi
    )
    
    print("Premiers lundis de chaque mois en 2023:")
    for dt in r:
        print(f"  - {dt.date()}")
    
    # Tous les vendredis 13 dans les 5 prochaines années
    start = DateUtils.parse("2023-01-01")
    friday_13th = DateUtils.rrule(
        Recurrence.MONTHLY,
        dtstart=start,
        count=20,  # Limiter à 20 occurrences
        byweekday=FR,
        bymonthday=13
    )
    
    print("\nVendredis 13 dans les prochaines années:")
    for dt in friday_13th:
        print(f"  - {dt.date()}")
    
    # 9. Fuseaux horaires
    print("\n9. Fuseaux horaires:")
    
    # UTC
    utc_now = datetime.datetime.now(DateUtils.utc())
    print(f"Heure UTC actuelle: {utc_now}")
    
    # Fuseau horaire local
    local_now = datetime.datetime.now(DateUtils.local_timezone())
    print(f"Heure locale actuelle: {local_now}")
    
    # 10. Exemple complet (comme dans l'exemple de dateutil)
    print("\n10. Exemple complet:")
    
    # Simuler l'exemple de dateutil "Prochaine Pâques lors d'une année avec un vendredi 13 en août"
    now = DateUtils.parse("2023-04-15")
    today = now.date()
    
    # Trouver la prochaine année avec un vendredi 13 en août
    year_with_friday_13th = DateUtils.rrule(
        Recurrence.YEARLY,
        dtstart=now,
        bymonth=8,
        bymonthday=13,
        byweekday=FR
    )[0].year
    
    # Calculer Pâques pour cette année
    easter_date = DateUtils.easter(year_with_friday_13th)
    
    # Calculer le delta relatif
    rdelta = RelativeDelta(today, easter_date)
    
    print(f"Aujourd'hui est: {today}")
    print(f"L'année avec le prochain vendredi 13 août est: {year_with_friday_13th}")
    print(f"Combien de temps jusqu'à Pâques de cette année: {rdelta}")
    print(f"Et la date de Pâques de cette année est: {today + rdelta}")
    
    print("\n=== FIN DES EXEMPLES ===\n")

# Exemple d'utilisation:
if __name__ == "__main__":
    samples()