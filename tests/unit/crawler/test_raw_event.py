from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate, build_content_hash


def test_build_content_hash_is_deterministic() -> None:
    first_hash = build_content_hash(
        source_name="SPATIC",
        source_url="https://example.test/detail/1",
        raw_title="title",
        raw_body="body",
    )
    second_hash = build_content_hash(
        source_name="SPATIC",
        source_url="https://example.test/detail/1",
        raw_title=" title ",
        raw_body=" body ",
    )

    assert first_hash == second_hash


def test_raw_event_candidate_fills_content_hash() -> None:
    candidate = RawEventCandidate(
        source_name="SPATIC",
        source_url="https://example.test/detail/1",
        raw_title="title",
        raw_body="body",
        raw_date_text="2026.07.04",
        raw_location_text="한강",
    )

    assert len(candidate.content_hash) == 64
