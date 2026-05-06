"""
Extended reputation decay + social reputation service coverage.
"""
import uuid
from datetime import datetime, timedelta

import pytest

from app.models.reputation import ReputationScore, ReputationEventType
from app.models.user import User, VerificationLevel, PrivacyMode
from app.services.reputation_decay_service import ReputationDecayService
from app.services.social_reputation_service import SocialReputationService
from app.schemas.reputation import FeedbackCreate


def _user(db) -> User:
    u = User(
        id=uuid.uuid4(),
        wallet_address=f"w_{uuid.uuid4().hex[:8]}",
        verification_level=VerificationLevel.WALLET,
        privacy_mode=PrivacyMode.SEMI_PRIVATE,
    )
    db.add(u)
    db.commit()
    return u


def _score(db, user: User, **kwargs) -> ReputationScore:
    defaults = dict(
        reliability_score=50.0,
        safety_score=50.0,
        response_score=50.0,
        meetup_completion_score=50.0,
        consent_confirmation_score=50.0,
    )
    defaults.update(kwargs)
    s = ReputationScore(id=uuid.uuid4(), user_id=user.id, **defaults)
    db.add(s)
    db.commit()
    return s


# ── apply_decay ───────────────────────────────────────────────────────────────

def test_no_decay_within_one_week(db):
    user = _user(db)
    s = _score(db, user, meetup_completion_score=60.0)
    s.last_decay_at = datetime.utcnow() - timedelta(days=3)
    db.commit()

    svc = ReputationDecayService(db)
    result = svc.apply_decay(user.id)
    assert result.meetup_completion_score == pytest.approx(60.0)


def test_decay_clamps_at_zero(db):
    user = _user(db)
    s = _score(db, user, safety_score=1.0)
    s.last_decay_at = datetime.utcnow() - timedelta(days=100)
    db.commit()

    svc = ReputationDecayService(db)
    result = svc.apply_decay(user.id)
    assert result.safety_score == pytest.approx(0.0)


def test_decay_returns_none_for_missing_score(db):
    user = _user(db)
    svc = ReputationDecayService(db)
    result = svc.apply_decay(user.id)
    assert result is None


def test_decay_uses_updated_at_when_last_decay_at_is_none(db):
    user = _user(db)
    s = _score(db, user, reliability_score=80.0)
    s.updated_at = datetime.utcnow() - timedelta(days=14)
    s.last_decay_at = None
    db.commit()

    svc = ReputationDecayService(db)
    result = svc.apply_decay(user.id)
    # 2 weeks × 1 pt decay → 78.0
    assert result.reliability_score == pytest.approx(78.0, abs=0.01)


# ── apply_bulk_decay ──────────────────────────────────────────────────────────

def test_bulk_decay_processes_stale_scores(db):
    users = [_user(db) for _ in range(3)]
    for u in users:
        s = _score(db, u)
        s.last_decay_at = datetime.utcnow() - timedelta(days=14)
        db.commit()

    # One fresh user — should not be processed
    fresh_user = _user(db)
    s_fresh = _score(db, fresh_user)
    s_fresh.last_decay_at = datetime.utcnow()
    db.commit()

    svc = ReputationDecayService(db)
    count = svc.apply_bulk_decay(days_inactive_threshold=7)
    assert count == 3


def test_bulk_decay_zero_when_all_fresh(db):
    user = _user(db)
    s = _score(db, user)
    s.last_decay_at = datetime.utcnow()
    db.commit()

    svc = ReputationDecayService(db)
    count = svc.apply_bulk_decay(days_inactive_threshold=7)
    assert count == 0


# ── SocialReputationService ───────────────────────────────────────────────────

def test_get_or_create_creates_new_score(db):
    user = _user(db)
    svc = SocialReputationService(db)

    score = svc.get_or_create(user.id)
    assert score.user_id == user.id
    assert score.id is not None


def test_get_or_create_is_idempotent(db):
    user = _user(db)
    svc = SocialReputationService(db)

    s1 = svc.get_or_create(user.id)
    s2 = svc.get_or_create(user.id)
    assert s1.id == s2.id


def test_record_feedback_meetup_completed_boosts_score(db):
    user = _user(db)
    svc = SocialReputationService(db)
    score = svc.get_or_create(user.id)
    original = score.meetup_completion_score

    ref_id = uuid.uuid4()
    svc.record_feedback(
        User(id=uuid.uuid4(), wallet_address="w_x", is_active=True),
        FeedbackCreate(
            target_user_id=user.id,
            reference_id=ref_id,
            event_type=ReputationEventType.MEETUP_COMPLETED,
        )
    )

    db.refresh(score)
    assert score.meetup_completion_score > original


def test_record_feedback_report_reduces_safety_score(db):
    user = _user(db)
    svc = SocialReputationService(db)
    score = svc.get_or_create(user.id)
    original_safety = score.safety_score

    reporter = User(id=uuid.uuid4(), wallet_address="w_r", is_active=True)
    svc.record_feedback(
        reporter,
        FeedbackCreate(
            target_user_id=user.id,
            reference_id=uuid.uuid4(),
            event_type=ReputationEventType.REPORT_RECEIVED,
        )
    )

    db.refresh(score)
    assert score.safety_score < original_safety


def test_record_meetup_completed_increments_total(db):
    user = _user(db)
    svc = SocialReputationService(db)
    svc.record_meetup_completed(user.id)
    svc.record_meetup_completed(user.id)

    score = svc.get_or_create(user.id)
    assert score.total_meetups == 2


def test_apply_delta_clamps_at_100(db):
    user = _user(db)
    svc = SocialReputationService(db)
    score = svc.get_or_create(user.id)
    score.reliability_score = 99.0
    svc._apply_delta(score, "reliability_score", 10.0)
    assert score.reliability_score == pytest.approx(100.0)


def test_apply_delta_clamps_at_zero(db):
    user = _user(db)
    svc = SocialReputationService(db)
    score = svc.get_or_create(user.id)
    score.safety_score = 2.0
    svc._apply_delta(score, "safety_score", -50.0)
    assert score.safety_score == pytest.approx(0.0)
