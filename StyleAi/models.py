from enum import Enum
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


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


@dataclass
class Outfit:
    id: int
    top: str
    bottom: str
    season: Season
    formality_level: FormalityLevel
    shoes: str = ""
    accessory: str = ""
    color_palette: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.top:
            raise ValueError()
        if not self.bottom:
            raise ValueError()

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


class ClothingItem:
    def __init__(self, item_id: int, name: str, color: str,
                 season: Season, formality: FormalityLevel):
        self._id = item_id
        self._name = name
        self._color = color
        self.season = season
        self.formality = formality

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError()
        self._name = value.strip()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value.strip().lower()

    def get_category(self) -> str:
        raise NotImplementedError()

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


class Shirt(ClothingItem):
    def __init__(self, item_id, name, color, season, formality,
                 sleeve_type: str = "long"):
        super().__init__(item_id, name, color, season, formality)
        self.sleeve_type = sleeve_type

    def get_category(self) -> str:
        return "top"

    def is_suitable_for(self, season: Season) -> bool:
        if self.sleeve_type == "short":
            return season in (Season.SPRING, Season.SUMMER)
        return True


class Pants(ClothingItem):
    def __init__(self, item_id, name, color, season, formality,
                 pant_type: str = "jeans"):
        super().__init__(item_id, name, color, season, formality)
        self.pant_type = pant_type

    def get_category(self) -> str:
        return "bottom"


class Shoes(ClothingItem):
    def __init__(self, item_id, name, color, season, formality,
                 shoe_type: str = "sneaker"):
        super().__init__(item_id, name, color, season, formality)
        self.shoe_type = shoe_type

    def get_category(self) -> str:
        return "shoes"


class Accessory(ClothingItem):
    def __init__(self, item_id, name, color, season, formality,
                 accessory_type: str = "bag"):
        super().__init__(item_id, name, color, season, formality)
        self.accessory_type = accessory_type

    def get_category(self) -> str:
        return "accessory"


@dataclass
class EventContext:
    event_type: EventType
    is_indoor: bool
    season: Season
    start_time: str = "09:00"
    end_time: str = "17:00"
    color_preference: str = ""

    def get_duration_hours(self) -> float:
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


class User:
    def __init__(self, user_id: int, email: str, gender: Gender,
                 name: str = ""):
        self._id = user_id
        self._email = email
        self._gender = gender
        self._name = name
        self._wardrobe: List[Outfit] = []

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def gender(self):
        return self._gender

    @property
    def name(self):
        return self._name

    def get_wardrobe(self) -> List[Outfit]:
        return list(self._wardrobe)

    def add_to_wardrobe(self, outfit: Outfit) -> None:
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
