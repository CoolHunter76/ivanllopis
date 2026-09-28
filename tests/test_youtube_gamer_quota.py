from youtube_gamer import _build_feed


def test_build_feed_keeps_public_recordings_and_live():
    details = [
        {
            "id": "live-id",
            "status": {"privacyStatus": "public", "embeddable": True},
            "snippet": {
                "title": "Live",
                "liveBroadcastContent": "live",
                "thumbnails": {},
            },
            "liveStreamingDetails": {"actualStartTime": "2026-09-28T10:00:00Z"},
        },
        {
            "id": "recording-id",
            "status": {"privacyStatus": "public", "embeddable": True},
            "snippet": {
                "title": "Recording",
                "liveBroadcastContent": "none",
                "thumbnails": {"medium": {"url": "https://example.test/thumb.jpg"}},
            },
        },
    ]

    live, recordings = _build_feed(details)

    assert live == {"video_id": "live-id", "title": "Live"}
    assert recordings == [
        {
            "video_id": "recording-id",
            "title": "Recording",
            "thumbnail": "https://example.test/thumb.jpg",
        }
    ]


def test_youtube_module_does_not_use_search_endpoint():
    source = __import__("pathlib").Path("youtube_gamer.py").read_text(encoding="utf-8")
    assert '_request(\n        "search"' not in source
    assert '"playlistItems"' in source
    assert '"videos"' in source
