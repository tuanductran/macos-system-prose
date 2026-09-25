"""Tests for collector execution."""

from __future__ import annotations

import asyncio

from prose.collector_runner import CollectorSpec, run_registered_collectors


async def _ok() -> object:
    return {"value": 1}


async def _fail() -> object:
    raise RuntimeError("boom")


async def _slow() -> object:
    await asyncio.sleep(0.05)
    return {}


def test_runner_records_success_and_failure() -> None:
    registry = (
        CollectorSpec("ok", _ok, {}, 1),
        CollectorSpec("fail", _fail, {}, 1),
    )
    collected, errors, status = asyncio.run(run_registered_collectors(registry))
    assert collected["ok"] == {"value": 1}
    assert collected["fail"] == {}
    assert errors == ["fail: RuntimeError: boom"]
    assert status["ok"]["status"] == "ok"
    assert status["fail"]["status"] == "error"


def test_runner_records_timeout() -> None:
    registry = (CollectorSpec("slow", _slow, [], 0.01),)
    collected, errors, status = asyncio.run(run_registered_collectors(registry))
    assert collected["slow"] == []
    assert errors == ["slow: CollectorTimeoutError: collector exceeded 0.01s timeout"]
    assert status["slow"]["status"] == "timeout"
    assert isinstance(status["slow"]["duration_ms"], float)


def test_runner_records_skipped_collectors() -> None:
    active = (CollectorSpec("active", _ok, {}, 1),)
    deep = (*active, CollectorSpec("skipped", _ok, [], 2))
    collected, errors, status = asyncio.run(
        run_registered_collectors(active, deep_registry=deep)
    )
    assert errors == []
    assert collected["skipped"] == []
    assert status["skipped"]["status"] == "skipped"
    assert status["skipped"]["timeout_seconds"] == 2
