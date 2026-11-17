import uuid
from datetime import UTC, datetime
from pathlib import Path

from bicycle_road_event_alarm.db.models import RawEvent
from bicycle_road_event_alarm.normalization.normalizer import normalize_raw_event


def make_raw_event(
    *,
    raw_title: str | None = "2026 한강 자전거 행사 교통통제 안내",
    raw_date_text: str | None = "2026.07.04 08:00 ~ 12:00",
    raw_location_text: str | None = "잠실대교 남단 ~ 뚝섬한강공원",
    raw_body: str | None = "한강 자전거 행사로 인해 일부 구간 교통통제가 예정되어 있습니다.",
    fetched_at: datetime = datetime(2026, 7, 3, 22, 30, tzinfo=UTC),
) -> RawEvent:
    return RawEvent(
        id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        source_name="서울경찰청 교통정보센터",
        source_url="https://example.test/detail/1",
        raw_title=raw_title,
        raw_body=raw_body,
        raw_date_text=raw_date_text,
        raw_location_text=raw_location_text,
        content_hash="hash",
        fetched_at=fetched_at,
        created_at=datetime(2026, 6, 30, tzinfo=UTC),
    )


def test_normalize_raw_event_builds_valid_publish_candidate() -> None:
    normalized = normalize_raw_event(make_raw_event())

    assert normalized.title == "2026 한강 자전거 행사 교통통제 안내"
    assert normalized.region == "서울"
    assert normalized.event_type == "road_closure"
    assert normalized.cyclist_impact_level == "high"
    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is True
    assert normalized.deterministic_duplicate_key


def test_normalize_raw_event_rejects_non_today_event_for_publish() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_date_text="2026.07.06 08:00 ~ 12:00",
            fetched_at=datetime(2026, 7, 4, 22, 30, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_allows_active_date_range_for_today_publish() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_date_text="2026-07-01(수) ~ 2026-07-05(일)",
            fetched_at=datetime(2026, 7, 4, 22, 30, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is True


def test_normalize_raw_event_publishes_active_ara_closure_from_abbreviated_body_range() -> None:
    raw_body = Path("tests/fixtures/crawler/ara_waterway_notice_1234.txt").read_text()
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title=(
                "(~'26. 12.) 아라뱃길 자전거도로 통행차단 알림 "
                "[(북)청운교-시천교-계양대교, 굴포천(서) 자전거길 구간] "
                "※ 주말 및 공휴일 포함"
            ),
            raw_date_text="2026-11-06",
            raw_location_text=None,
            raw_body=raw_body,
            fetched_at=datetime(2026, 11, 15, 21, 29, tzinfo=UTC),
        )
    )

    assert normalized.start_datetime == datetime(2026, 11, 9, 15, 0, tzinfo=UTC)
    assert normalized.end_datetime == datetime(2026, 12, 31, 14, 59, tzinfo=UTC)
    assert normalized.cyclist_impact_level == "high"
    assert normalized.validation_status == "needs_review"
    assert normalized.location_name == "구간 확인 필요"
    assert "청운교-시천교-계양대교" in normalized.title
    assert "굴포천(서) 자전거길" in normalized.title
    assert normalized.publish_candidate is True


def test_normalize_raw_event_excludes_ara_closure_after_abbreviated_body_range() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title=(
                "(~'26. 12.) 아라뱃길 자전거도로 통행차단 알림 "
                "[(북)청운교-시천교-계양대교, 굴포천(서) 자전거길 구간] "
                "※ 주말 및 공휴일 포함"
            ),
            raw_date_text="2026-11-06",
            raw_location_text=None,
            raw_body=(
                "자전거도로 포장 보수공사로 자전거도로를 차단합니다. "
                "차단기간 '26. 11. 10.(화) ~ '26. 12. 31.(목)"
            ),
            fetched_at=datetime(2027, 1, 1, 0, 0, tzinfo=UTC),
        )
    )

    assert normalized.publish_candidate is False


def test_normalize_raw_event_marks_missing_date_invalid() -> None:
    normalized = normalize_raw_event(make_raw_event(raw_date_text=None))

    assert normalized.validation_status == "invalid"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_marks_missing_location_needs_review() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title="2026 자전거 행사 교통통제 안내",
            raw_location_text=None,
            raw_body="일부 구간 교통통제가 예정되어 있습니다.",
        )
    )

    assert normalized.validation_status == "needs_review"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_publishes_direct_bicycle_road_closure_without_location() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title="아라뱃길 자전거도로 통행 차단 알림",
            raw_location_text=None,
            raw_body="자전거도로 일부 구간 통행 차단 예정입니다.",
        )
    )

    assert normalized.validation_status == "needs_review"
    assert normalized.location_name == "구간 확인 필요"
    assert normalized.publish_candidate is True


def test_normalize_raw_event_publishes_weather_closure_until_conditions_improve() -> None:
    location_text = "시천교~계양대교 남, 북측 자전거도로"
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title=(
                "자전거도로, 아라마루 전망대 및 아라폭포 통행 차단 알림 "
                "(7.9(목) 13:00 ~ 기상 여건 완화 시)"
            ),
            raw_date_text="2026-07-09",
            raw_location_text=location_text,
            raw_body=(
                "금일 강우예보로 인하여 이용객 안전을 위해 자전거도로 등 출입 차단 중입니다. "
                "<차단기간> 7.9(목) 13:00 ~ 기상 여건 완화 시"
            ),
            fetched_at=datetime(2026, 7, 9, 23, 41, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.location_name == location_text
    assert normalized.region == "경기"
    assert normalized.publish_candidate is True


def test_normalize_raw_event_uses_ara_detail_blocked_sections_as_location() -> None:
    location_text = (
        "시천교~계양대교 남, 북측 자전거도로; "
        "굴포천 연결수로 좌안(서측) 자전거도로; "
        "아라마루 전망대 및 아라폭포"
    )

    normalized = normalize_raw_event(
        make_raw_event(
            raw_title=(
                "자전거도로, 아라마루 전망대 및 아라폭포 통행 차단 알림 "
                "(7.17(금) 21:30 ~ 기상 여건 완화 시)"
            ),
            raw_date_text="2026-07-17",
            raw_location_text=location_text,
            raw_body=(
                "금일~명일 강우예보로 인하여 이용객 안전을 위해 자전거도로 등 출입 차단 중입니다. "
                "<차단기간> 7.17(금) 21:30 ~ 기상 여건 완화 시"
            ),
            fetched_at=datetime(2026, 7, 19, 22, 30, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.location_name == location_text
    assert normalized.region == "경기"
    assert normalized.publish_candidate is True


def test_normalize_raw_event_extracts_ara_weather_standard_sections_from_body() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title="강우 및 강설에 따른 친수시설(자전거도로, 전망대 등) 통행차단 기준 알림",
            raw_date_text="2026-08-28",
            raw_location_text=None,
            raw_body=(
                "아라뱃길 이용객에 안전한 친수 공간 제공을 위하여, 강우 및 강설시 "
                "기상 여건에 따라 아래와 같이 친수시설 통행을 차단함을 알려드립니다. "
                "□ 강우 시 친수시설 차단 기준 "
                "-(아라마루 전망대) 강우 발생 즉시 및 미끄럼의 위험이 있는 경우 "
                "-(아라폭포 철재계단) 강우 발생 즉시 및 미끄럼의 위험이 있는 경우 "
                "-(굴포천 연결수로 자전거도로) 강우 발생 즉시 "
                "-(북측 자전거도로 시천교~계양대교) 10~20mm 이상 예보시 "
                "-(남측 자전거도로 시천교~야생화테라스) 10~20mm 이상 예보시 "
                "□ 강설 시 친수시설 차단 기준 "
                "-(아라마루 전망대) 강설 발생 즉시 및 미끄럼의 위험이 있는 경우 "
                "-(아라폭포 철재계단) 강설 발생 즉시 및 미끄럼의 위험이 있는 경우 "
                "-(굴포천 연결수로 자전거도로) 강설 발생 즉시 "
                "-(북측 자전거도로 시천교~계양대교) 강설 발생 즉시 "
                "-(남측 자전거도로 시천교~야생화테라스) 강설 발생 즉시"
            ),
            fetched_at=datetime(2026, 8, 27, 23, 10, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.region == "경기"
    assert normalized.location_name == (
        "아라뱃길 친수시설(아라마루 전망대, 아라폭포 철재계단, "
        "굴포천 연결수로 자전거도로, 북측 자전거도로 시천교~계양대교 등)"
    )
    assert normalized.publish_candidate is True


def test_normalize_raw_event_does_not_publish_completed_indefinite_closure() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title=(
                "자전거도로, 아라마루 전망대 및 아라폭포 통행 차단 알림 "
                "(6.19. 18:00 ~ 기상 여건 완화 시) [개방완료]"
            ),
            raw_date_text="2026-06-19",
            raw_location_text="시천교~계양대교 남, 북측 자전거도로",
            raw_body="기상 여건 완화 시까지 통행 차단합니다.",
            fetched_at=datetime(2026, 7, 9, 23, 41, tzinfo=UTC),
        )
    )

    assert normalized.publish_candidate is False
