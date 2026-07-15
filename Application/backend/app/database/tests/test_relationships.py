"""One-to-many and many-to-many relationship navigation."""

from datetime import datetime, timedelta

from database.enums import MembershipStatus, UserRole
from database.models.auth import User
from database.models.clubs import Club, ClubMembership, Committee, CommitteeMembership
from database.models.events import Event, EventRegistration
from database.models.external_relations import ClubSponsor, Sponsor


def _make_user(session, email, role=UserRole.STUDENT):
    user = User(email=email, password_hash="hash", full_name="Test User", role=role)
    session.add(user)
    session.commit()
    return user


def test_one_to_many_club_to_events(session, sample_university):
    advisor = _make_user(session, "advisor@example.com")
    club = Club(name="Robotics", slug="robotics", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    e1 = Event(club_id=club.id, title="Kickoff", start_at=datetime.utcnow(),
               end_at=datetime.utcnow() + timedelta(hours=1), created_by=advisor.id)
    e2 = Event(club_id=club.id, title="Demo Day", start_at=datetime.utcnow(),
               end_at=datetime.utcnow() + timedelta(hours=1), created_by=advisor.id)
    session.add_all([e1, e2])
    session.commit()

    assert len(club.events) == 2
    assert e1.club.name == "Robotics"


def test_one_to_many_user_to_memberships(session, sample_university):
    advisor = _make_user(session, "advisor2@example.com")
    student = _make_user(session, "student@example.com")
    club_a = Club(name="Art Club", slug="art-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    club_b = Club(name="Music Club", slug="music-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add_all([club_a, club_b])
    session.commit()

    session.add_all([
        ClubMembership(user_id=student.id, club_id=club_a.id, status=MembershipStatus.APPROVED),
        ClubMembership(user_id=student.id, club_id=club_b.id, status=MembershipStatus.PENDING),
    ])
    session.commit()

    assert len(student.club_memberships) == 2


def test_many_to_many_committee_membership(session, sample_university):
    advisor = _make_user(session, "advisor3@example.com")
    club = Club(name="Debate Club", slug="debate-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    student1 = _make_user(session, "d1@example.com")
    student2 = _make_user(session, "d2@example.com")
    m1 = ClubMembership(user_id=student1.id, club_id=club.id, status=MembershipStatus.APPROVED)
    m2 = ClubMembership(user_id=student2.id, club_id=club.id, status=MembershipStatus.APPROVED)
    session.add_all([m1, m2])
    session.commit()

    committee = Committee(club_id=club.id, name="Organizing Committee")
    session.add(committee)
    session.commit()

    session.add_all([
        CommitteeMembership(committee_id=committee.id, membership_id=m1.id),
        CommitteeMembership(committee_id=committee.id, membership_id=m2.id),
    ])
    session.commit()

    assert len(committee.member_links) == 2
    assert {link.membership.user_id for link in committee.member_links} == {student1.id, student2.id}


def test_many_to_many_club_sponsor(session, sample_university):
    advisor = _make_user(session, "advisor4@example.com")
    club_a = Club(name="Coding Club", slug="coding-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    club_b = Club(name="Gaming Club", slug="gaming-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add_all([club_a, club_b])
    session.commit()

    sponsor = Sponsor(organization_name="Globex")
    session.add(sponsor)
    session.commit()

    session.add_all([
        ClubSponsor(club_id=club_a.id, sponsor_id=sponsor.id),
        ClubSponsor(club_id=club_b.id, sponsor_id=sponsor.id),
    ])
    session.commit()

    # One sponsor supports multiple clubs
    assert len(sponsor.club_links) == 2
    assert {link.club.name for link in sponsor.club_links} == {"Coding Club", "Gaming Club"}


def test_event_registration_relationship(session, sample_university):
    advisor = _make_user(session, "advisor5@example.com")
    student = _make_user(session, "student5@example.com")
    club = Club(name="Photography Club", slug="photo-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    event = Event(club_id=club.id, title="Photo Walk", start_at=datetime.utcnow(),
                  end_at=datetime.utcnow() + timedelta(hours=1), created_by=advisor.id)
    session.add(event)
    session.commit()

    registration = EventRegistration(event_id=event.id, user_id=student.id)
    session.add(registration)
    session.commit()

    assert event.registrations[0].user.email == student.email
