"""
models.py
---------
UML class diagram'dan birebir türetilmiş veri modelleri.
Encapsulation, Inheritance ve Polymorphism örneklerini içerir.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# ─── ENUM TANIMLAMALARI ──────────────────────────────────────────────────────

class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class FormalityLevel(Enum):
    CASUAL = "casual"
    SMART = "smart"
    FORMAL = "formal"
    SPORTY = "sporty"


class EventType(Enum):
    WORK = "work"
    CASUAL = "casual"
    SPORT = "sport"
    FORMAL = "formal"
    OUTDOOR = "outdoor"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ─── OUTFIT (UML'den birebir) ─────────────────────────────────────────────────

@dataclass
class Outfit:
    """
    UML: Outfit
    +id: int
    +top: String
    +bottom: String
    +season: Season
    +formalityLevel: FormalityLevel

    Encapsulation: tüm alanlar __init__ üzerinden kontrollü set edilir.
    """
    id: int
    top: str
    bottom: str
    season: Season
    formality_level: FormalityLevel
    shoes: str = ""
    accessory: str = ""
    color_palette: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # ── Encapsulation: property ile doğrulama ───────────────────────────────
    def __post_init__(self):
        if not self.top:
            raise ValueError("Outfit mutlaka bir üst parça içermelidir.")
        if not self.bottom:
            raise ValueError("Outfit mutlaka bir alt parça içermelidir.")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "top": self.top,
            "bottom": self.bottom,
            "shoes": self.shoes,
            "accessory": self.accessory,
            "season": self.season.value,
            "formality_level": self.formality_level.value,
            "color_palette": self.color_palette,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return (f"Outfit(id={self.id}, top='{self.top}', "
                f"bottom='{self.bottom}', season={self.season.value})")


# ─── CLOTHING ITEM (Inheritance tabanı) ──────────────────────────────────────

class ClothingItem:
    """
    Temel giysi sınıfı.
    Inheritance: Shirt, Pants, Shoes, Accessory bu sınıftan türer.
    Encapsulation: _name ve _color private alanlar.
    """

    def __init__(self, item_id: int, name: str, color: str,
                 season: Season, formality: FormalityLevel):
        self._id = item_id  # encapsulation: private
        self._name = name
        self._color = color
        self.season = season
        self.formality = formality

    # ── Property getter / setter (Encapsulation) ────────────────────────────
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Parça adı boş olamaz.")
        self._name = value.strip()

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value.strip().lower()

    # ── Polymorphism: alt sınıflar override eder ────────────────────────────
    def get_category(self) -> str:
        raise NotImplementedError("Alt sınıf get_category() tanımlamalıdır.")

    def is_suitable_for(self, season: Season) -> bool:
        return self.season == season

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "name": self._name,
            "color": self._color,
            "season": self.season.value,
            "formality": self.formality.value,
            "category": self.get_category(),
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self._name}', color='{self._color}')"


# ── Alt sınıflar (Inheritance + Polymorphism) ──────────────────────────────

class Shirt(ClothingItem):
    """Üst giysi — ClothingItem'dan türer."""

    def __init__(self, item_id, name, color, season, formality,
                 sleeve_type: str = "long"):
        super().__init__(item_id, name, color, season, formality)
        self.sleeve_type = sleeve_type  # sadece Shirt'e özgü alan

    def get_category(self) -> str:  # Polymorphism override
        return "top"

    def is_suitable_for(self, season: Season) -> bool:
        if self.sleeve_type == "short":
            return season in (Season.SPRING, Season.SUMMER)
        return True  # uzun kollu her mevsim


class Pants(ClothingItem):
    """Alt giysi."""

    def __init__(self, item_id, name, color, season, formality,
                 pant_type: str = "jeans"):
        super().__init__(item_id, name, color, season, formality)
        self.pant_type = pant_type

    def get_category(self) -> str:
        return "bottom"


class Shoes(ClothingItem):
    """Ayakkabı."""

    def __init__(self, item_id, name, color, season, formality,
                 shoe_type: str = "sneaker"):
        super().__init__(item_id, name, color, season, formality)
        self.shoe_type = shoe_type

    def get_category(self) -> str:
        return "shoes"

    def is_suitable_for(self, season: Season) -> bool:
        if self.shoe_type == "sandal":
            return season in (Season.SPRING, Season.SUMMER)
        if self.shoe_type == "boot":
            return season in (Season.AUTUMN, Season.WINTER)
        return True


class Accessory(ClothingItem):
    """Aksesuar."""

    def __init__(self, item_id, name, color, season, formality,
                 accessory_type: str = "bag"):
        super().__init__(item_id, name, color, season, formality)
        self.accessory_type = accessory_type

    def get_category(self) -> str:
        return "accessory"


# ─── EVENT CONTEXT (UML'den birebir) ─────────────────────────────────────────

@dataclass
class EventContext:
    """
    UML: EventContext
    +eventType: EventType
    +isIndoor: boolean
    +season: Season
    """
    event_type: EventType
    is_indoor: bool
    season: Season
    start_time: str = "09:00"
    end_time: str = "17:00"
    color_preference: str = ""

    def get_duration_hours(self) -> float:
        """Dışarıda kalınacak süreyi hesapla."""
        try:
            sh, sm = map(int, self.start_time.split(":"))
            eh, em = map(int, self.end_time.split(":"))
            return max(0.0, (eh * 60 + em - sh * 60 - sm) / 60)
        except ValueError:
            return 0.0

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "is_indoor": self.is_indoor,
            "season": self.season.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "color_preference": self.color_preference,
            "duration_hours": self.get_duration_hours(),
        }


# ─── USER (UML'den birebir) ───────────────────────────────────────────────────

class User:
    """
    UML: User
    +id: int
    +email: String
    +gender: Gender
    +getWardrobe(): List<Outfit>

    Encapsulation: _wardrobe dışarıdan doğrudan erişilemiyor.
    """

    def __init__(self, user_id: int, email: str, gender: Gender,
                 name: str = ""):
        self._id = user_id
        self._email = email
        self._gender = gender
        self._name = name
        self._wardrobe: List[Outfit] = []  # private

    # ── Encapsulation: property'ler ─────────────────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def email(self) -> str:
        return self._email

    @property
    def gender(self) -> Gender:
        return self._gender

    @property
    def name(self) -> str:
        return self._name

    # ── UML metodu: getWardrobe() ────────────────────────────────────────────
    def get_wardrobe(self) -> List[Outfit]:
        return list(self._wardrobe)  # kopya döndür (encapsulation)

    def add_to_wardrobe(self, outfit: Outfit) -> None:
        if not isinstance(outfit, Outfit):
            raise TypeError("Sadece Outfit nesnesi eklenebilir.")
        self._wardrobe.append(outfit)

    def remove_from_wardrobe(self, outfit_id: int) -> bool:
        for i, o in enumerate(self._wardrobe):
            if o.id == outfit_id:
                self._wardrobe.pop(i)
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "email": self._email,
            "name": self._name,
            "gender": self._gender.value,
            "wardrobe_count": len(self._wardrobe),
        }

    def __repr__(self):
        return f"User(id={self._id}, email='{self._email}')"
