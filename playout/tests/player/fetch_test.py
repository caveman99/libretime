from queue import Queue
from unittest.mock import MagicMock, call

from libretime_playout.config import Config
from libretime_playout.liquidsoap.client import LiquidsoapClientError
from libretime_playout.player.fetch import PypoFetch


def make_fetch(config: Config, liquidsoap: MagicMock) -> PypoFetch:
    api_client = MagicMock()
    api_client.get_info.return_value.json.return_value = {"station_name": "LibreTime"}
    api_client.get_stream_preferences.return_value.json.return_value = {
        "input_fade_transition": 0.0,
        "message_format": 0,
        "message_offline": "",
        "replay_gain_enabled": True,
        "replay_gain_offset": 0.0,
        "metadata_router_enabled": False,
    }
    api_client.get_stream_state.return_value.json.return_value = {
        "input_main_connected": False,
        "input_main_streaming": False,
        "input_show_connected": False,
        "input_show_streaming": False,
        "schedule_streaming": True,
    }
    return PypoFetch(
        Queue(),
        Queue(),
        Queue(),
        MagicMock(),
        liquidsoap,
        config,
        api_client,
        MagicMock(),
    )


def test_fetch_thread(config: Config):
    PypoFetch(
        Queue(),
        Queue(),
        Queue(),
        MagicMock(),
        MagicMock(),
        config,
        MagicMock(),
        MagicMock(),
    )


def test_set_bootstrap_variables_waits_for_liquidsoap(config: Config):
    liquidsoap = MagicMock()
    make_fetch(config, liquidsoap).set_bootstrap_variables()

    liq_client = liquidsoap.liq_client
    assert liq_client.method_calls[0] == call.wait_for_version(timeout=120)
    liq_client.source_switch_status.assert_any_call(
        name="scheduled_play", streaming=True
    )


def test_set_bootstrap_variables_liquidsoap_unavailable(config: Config):
    liquidsoap = MagicMock()
    liquidsoap.liq_client.wait_for_version.side_effect = LiquidsoapClientError()
    make_fetch(config, liquidsoap).set_bootstrap_variables()

    liquidsoap.liq_client.source_switch_status.assert_not_called()
    liquidsoap.clear_queue_tracker.assert_called_once()
