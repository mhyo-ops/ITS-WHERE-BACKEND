from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db import models
from app.db.base import SessionLocal
from app.db.init_db import init_db


def _find_category_by_name(db: Session, name: str) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.name == name).first()


def _find_event_by_title(db: Session, title: str) -> models.Event | None:
    return db.query(models.Event).filter(models.Event.title == title).first()


def _find_admin_by_slug(db: Session, slug: str) -> models.AdminUser | None:
    return db.query(models.AdminUser).filter(models.AdminUser.admin_slug == slug).first()


def _find_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def _find_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        print("Seeding categories...")
        categories = [
            ("sport", "Activités sportives pour renforcer l'esprit d'équipe et la santé."),
            ("culture", "Événements culturels pour célébrer les arts et traditions locales."),
            ("volontariat", "Actions de volontariat pour soutenir les initiatives communautaires."),
            ("education", "Programmes éducatifs pour améliorer les compétences et l'employabilité."),
            ("art", "Ateliers artistiques qui stimulent la créativité et l'expression personnelle."),
            ("sante", "Initiatives santé pour promouvoir le bien-être physique et mental."),
            ("environnement", "Projets environnementaux pour protéger la nature et les espaces publics."),
            ("technologie", "Activités technologiques pour encourager l'innovation et les nouvelles compétences."),
        ]

        seeded_categories = 0
        for name, description in categories:
            if _find_category_by_name(db, name) is None:
                category = models.Category(name=name, description=description)
                db.add(category)
                db.commit()
                seeded_categories += 1
        print(f"Seeded categories: {seeded_categories}")

        print("Seeding events...")
        event_definitions: List[Dict[str, object]] = [
            {
                "title": "Festival Sportif de la Jeunesse",
                "title_ar": "مهرجان الشباب الرياضي",
                "category": "sport",
                "description_fr": (
                    "Un festival sportif dédié aux jeunes avec tournois et ateliers. "
                    "L'événement met l'accent sur la participation et la forme physique."
                ),
                "wilaya": "Bejaia",
            },
            {
                "title": "Atelier d'Écriture Culturelle",
                "title_ar": "ورشة الكتابة الثقافية",
                "category": "culture",
                "description_fr": (
                    "Une journée d'écriture pour explorer la littérature et les traditions. "
                    "Les jeunes créent des textes en groupe et partagent leurs idées."
                ),
                "wilaya": "Bejaia",
            },
            {
                "title": "Journée Volontariat Écologique",
                "title_ar": "يوم التطوع البيئي",
                "category": "volontariat",
                "description_fr": (
                    "Une action citoyenne pour nettoyer et embellir les espaces urbains. "
                    "Les participants agissent ensemble pour l'environnement local."
                ),
                "wilaya": "Setif",
            },
            {
                "title": "Forum Éducatif Numérique",
                "title_ar": "منتدى التعليم الرقمي",
                "category": "education",
                "description_fr": (
                    "Un forum sur les opportunités numériques et la formation technologique. "
                    "Des ateliers pratiques aident à maîtriser les outils modernes."
                ),
                "wilaya": "Setif",
            },
            {
                "title": "Exposition d'Art Urbain",
                "title_ar": "معرض الفن الحضري",
                "category": "art",
                "description_fr": (
                    "Une exposition mettant en lumière le street art et la création contemporaine. "
                    "Les jeunes artistes exposent leurs œuvres à un large public."
                ),
                "wilaya": "Alger",
            },
            {
                "title": "Clinique Santé Jeunes",
                "title_ar": "عيادة صحة الشباب",
                "category": "sante",
                "description_fr": (
                    "Une clinique mobile offrant des conseils santé et des dépistages gratuits. "
                    "Des professionnels animent des sessions sur le bien-être quotidien."
                ),
                "wilaya": "Alger",
            },
            {
                "title": "Camp Environnemental",
                "title_ar": "المخيم البيئي",
                "category": "environnement",
                "description_fr": (
                    "Un camp dédié à la sensibilisation écologique et au travail de terrain. "
                    "Les participants plantent des arbres et apprennent à préserver la nature."
                ),
                "wilaya": "Tizi Ouzou",
            },
            {
                "title": "Hackathon Technologie",
                "title_ar": "هاكاثون التكنولوجيا",
                "category": "technologie",
                "description_fr": (
                    "Un hackathon pour développer des solutions numériques en équipe. "
                    "Les jeunes présentent des prototypes et reçoivent des retours de mentors."
                ),
                "wilaya": "Tizi Ouzou",
            },
            {
                "title": "Match de Basket Interquartier",
                "title_ar": "مباراة كرة السلة بين الأحياء",
                "category": "sport",
                "description_fr": (
                    "Un tournoi de basket rassemblant des équipes de quartiers voisins. "
                    "Il favorise le fair-play et la cohésion entre les jeunes."
                ),
                "wilaya": "Oran",
            },
            {
                "title": "Atelier Cinéma et Culture",
                "title_ar": "ورشة السينما والثقافة",
                "category": "culture",
                "description_fr": (
                    "Un atelier de création filmique axé sur la culture locale. "
                    "Les participants réalisent de courts métrages en équipe."
                ),
                "wilaya": "Oran",
            },
            {
                "title": "Journée Volontariat Communautaire",
                "title_ar": "يوم التطوع المجتمعي",
                "category": "volontariat",
                "description_fr": (
                    "Une journée d'engagement social pour soutenir les initiatives de quartier. "
                    "Le programme met en relation jeunes bénévoles et associations locales."
                ),
                "wilaya": "Constantine",
            },
            {
                "title": "Session de Formation Technologique",
                "title_ar": "جلسة التدريب التكنولوجي",
                "category": "technologie",
                "description_fr": (
                    "Une formation pratique sur le développement d'applications et le numérique. "
                    "Les participants explorent des cas concrets et des outils innovants."
                ),
                "wilaya": "Constantine",
            },
        ]

        seeded_events = 0
        for index, event_data in enumerate(event_definitions, start=1):
            if _find_event_by_title(db, event_data["title"]) is not None:
                continue

            category = _find_category_by_name(db, event_data["category"])
            if category is None:
                continue

            event = models.Event(
                category_id=category.id,
                title=event_data["title"],
                title_fr=event_data["title"],
                title_ar=event_data.get("title_ar"),
                description=event_data["description_fr"],
                description_fr=event_data["description_fr"],
                description_ar=event_data.get("description_ar"),
                address=f"Centre culturel {event_data['wilaya']}",
                postal_code="06000",
                commune="Centre-ville",
                wilaya=event_data["wilaya"],
                date_begin=datetime.utcnow() + timedelta(days=30 * index),
                date_end=None,
                capacity=20 + ((index - 1) % 5) * 16,
                remaining_spots=20 + ((index - 1) % 5) * 16,
                registration_link=None,
                registration_contact=None,
                registration_required=(index % 2 == 0),
                is_volunteering=(event_data["category"] == "volontariat"),
                volunteer_skills=None,
                cost="Gratuit",
                status="upcoming",
                is_active=True,
            )
            db.add(event)
            db.commit()
            seeded_events += 1
        print(f"Seeded events: {seeded_events}")

        print("Seeding admin user...")
        if _find_admin_by_slug(db, "admin_odej") is None:
            admin = models.AdminUser(
                admin_slug="admin_odej",
                hashed_password=hash_password("Admin2026!"),
            )
            db.add(admin)
            db.commit()
        print("Admin user present: True")

        print("Seeding test user...")
        if _find_user_by_email(db, "test@odej.dz") is None and _find_user_by_username(db, "testuser") is None:
            user = models.User(
                email="test@odej.dz",
                username="testuser",
                preferred_language="fr",
                postal_code="06000",
                hashed_password=hash_password("Test2026!"),
                is_active=True,
            )
            db.add(user)
            db.commit()
        print("Test user present: True")

        print(f"✅ Seeded: {seeded_categories} categories, {seeded_events} events, 1 admin, 1 user")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
