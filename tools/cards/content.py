"""The words on the cards. Every claim here is checked against career/master_profile.yaml."""

from dataclasses import dataclass

TILE_COLOUR_NAMES = ("blue", "red", "yellow")
LANGUAGES = ("java", "typescript")


def _require_choice(field: str, value: str, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        raise ValueError(f"Unknown {field} '{value}'; use one of: {', '.join(allowed)}")


@dataclass(frozen=True)
class Hero:
    kicker: str
    first: str
    last: str
    tagline: str
    link: str


@dataclass(frozen=True)
class Tile:
    slug: str
    label: str
    number: str
    unit: str  # set in italic after the number; may be empty
    body: str
    colour: str  # "blue", "red" or "yellow"

    def __post_init__(self) -> None:
        _require_choice("colour", self.colour, TILE_COLOUR_NAMES)


@dataclass(frozen=True)
class Project:
    slug: str
    name: str
    body: str
    foot: str
    language: str  # "java" or "typescript"

    def __post_init__(self) -> None:
        _require_choice("language", self.language, LANGUAGES)


@dataclass(frozen=True)
class Heading:
    slug: str
    plain: str
    italic: str


HERO = Hero(
    kicker="BACKEND DEVELOPER AT INTELLIGENTDX",
    first="Vaibhav",
    last="Jain",
    tagline="I build booking and scheduling APIs on Google Cloud, and Java microservices on the side.",
    link="vaibhavjain-portfolio.vercel.app ↗",
)

TILES = (
    Tile(
        slug="booking",
        label="BOOKING",
        number="15",
        unit="lanes",
        body="One endpoint books every visit of a treatment plan, up to 15 lanes in parallel. "
        "In production since September 2026.",
        colour="blue",
    ),
    Tile(
        slug="sync",
        label="SYNC",
        number="213 × 111 × 70",
        unit="",
        body="Providers × locations × visit types, synced by Cloud Run Jobs into PostgreSQL.",
        colour="red",
    ),
    Tile(
        slug="speed",
        label="SPEED",
        number="1.7–2.5",
        unit="s",
        body="Slot search, down from 2.7–3.6 s with a concurrent pager.",
        colour="yellow",
    ),
)

PROJECTS = (
    Project(
        slug="voting",
        name="Voting_System",
        body="Online elections where every vote is SHA-256 chained to the one before it, "
        "across 6 Spring Boot services.",
        foot="Java · Spring Boot",
        language="java",
    ),
    Project(
        slug="courier",
        name="Courier-management-system",
        body="Delivery platform with Admin, User and Delivery Partner modules, "
        "secured with Spring Security and JWT.",
        foot="Java · Spring Boot",
        language="java",
    ),
    Project(
        slug="portfolio",
        name="Portfolio",
        body="My portfolio site: experience, projects and CV.",
        foot="TypeScript · live",
        language="typescript",
    ),
)

HEADING = Heading(slug="building", plain="What I’m", italic="building")
