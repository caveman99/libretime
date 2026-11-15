from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from dateutil.tz import tzutc

from libretime_playout.player.events import EventKind, FileEvent
from libretime_playout.player.liquidsoap import Liquidsoap, create_liquidsoap_annotation


@patch("libretime_playout.player.events.CACHE_DIR", Path("/fake"))
def test_create_liquidsoap_annotation():
    file_event = FileEvent(
        type=EventKind.FILE,
        row_id=1,
        start=datetime(2022, 9, 5, 11, tzinfo=tzutc()),
        end=datetime(2022, 9, 5, 11, 5, 2, tzinfo=tzutc()),
        uri=None,
        id=2,
        show_name="Show 1",
        fade_in=500.0,
        fade_out=500.0,
        cue_in=13.7008,
        cue_out=315.845,
        track_title='My Friend the "Forest"',
        artist_name="Nils Frahm",
        mime="audio/flac",
        replay_gain=11.46,
        filesize=10000,
    )

    assert create_liquidsoap_annotation(file_event) == (
        "annotate:"
        'media_id="2",'
        'schedule_table_id="1",'
        'liq_start_next="0",'
        'liq_fade_in="0.5",'
        'liq_fade_out="0.5",'
        'liq_cue_in="13.7008",'
        'liq_cue_out="315.845",'
        'replay_gain="11.46 dB",'
        'artist="Nils Frahm",'
        'title="My Friend the \\"Forest\\""'
        ":/fake/2.flac"
    )

    file_event.artist_name = "New\nline to space"
    file_event.track_title = "Trailing\nnewline\n"

    assert create_liquidsoap_annotation(file_event) == (
        "annotate:"
        'media_id="2",'
        'schedule_table_id="1",'
        'liq_start_next="0",'
        'liq_fade_in="0.5",'
        'liq_fade_out="0.5",'
        'liq_cue_in="13.7008",'
        'liq_cue_out="315.845",'
        'replay_gain="11.46 dB",'
        'artist="New line to space",'
        'title="Trailing newline"'
        ":/fake/2.flac"
    )


def test_liquidsoap():
    Liquidsoap(MagicMock())


def test_liquidsoap_push_in_progress_not_duplicated():
    file_event = FileEvent(
        type=EventKind.FILE,
        row_id=1,
        start=datetime(2022, 9, 5, 11),
        end=datetime(2099, 9, 5, 11),
        id=2,
        show_name="Show 1",
        fade_in=500.0,
        fade_out=500.0,
        cue_in=0.0,
        cue_out=3600.0,
        mime="audio/mp4",
        filesize=10000,
        file_ready=True,
    )
    liquidsoap = Liquidsoap(MagicMock())

    # The other thread pushes the same item while the first push is still running.
    push = MagicMock(side_effect=lambda *_: liquidsoap.play(file_event))
    liquidsoap.telnet_liquidsoap.queue_push = push
    liquidsoap.play(file_event)

    push.assert_called_once()
    assert list(liquidsoap.liq_queue_tracker.values()).count(file_event) == 1
