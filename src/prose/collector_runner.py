"""Shared execution machinery for macOS System Prose collectors."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from prose import utils
from prose.schema import CollectionStatus

@dataclass(frozen=True)
class CollectorSpec:
    """Typed registration for one independent report collector."""

    name: str
    run: Callable[[], Awaitable[object]]
    default: object
    timeout_seconds: float


class CollectorTimeoutError(TimeoutError):
    """Raised when a collector exceeds its configured execution timeout."""

    def __init__(self, message: str, duration_ms: float) -> None:
        super().__init__(message)
        self.duration_ms = duration_ms


def _async_collector(collector: Callable[[], object]) -> Callable[[], Awaitable[object]]:
    """Adapt a synchronous collector to the async collector registry."""

    async def run_collector() -> object:
        return await asyncio.to_thread(collector)

    return run_collector


async def run_registered_collectors(
    registry: tuple[CollectorSpec, ...],
    *,
    deep_registry: tuple[CollectorSpec, ...] | None = None,
) -> tuple[dict[str, object], list[str], dict[str, CollectionStatus]]:
    """Execute registered collectors and return data plus collection metadata."""
    results = await asyncio.gather(
        *(run_collector(spec) for spec in registry),
        return_exceptions=True,
    )

    collection_errors: list[str] = []
    collection_status: dict[str, CollectionStatus] = {}
    collected: dict[str, object] = {}

    if deep_registry is not None:
        active_names = {spec.name for spec in registry}
        for spec in deep_registry:
            if spec.name not in active_names:
                collection_status[spec.name] = {
                    "status": "skipped",
                    "error": None,
                    "duration_ms": None,
                    "timeout_seconds": spec.timeout_seconds,
                }
                collected[spec.name] = spec.default

    for spec, result in zip(registry, results, strict=False):
        if isinstance(result, BaseException):
            error_message = f"{type(result).__name__}: {result!s}"
            status: Literal["ok", "error", "timeout", "skipped"] = (
                "timeout" if isinstance(result, TimeoutError) else "error"
            )
            collection_errors.append(f"{spec.name}: {error_message}")
            collection_status[spec.name] = {
                "status": status,
                "error": error_message,
                "duration_ms": round(result.duration_ms, 3)
                if isinstance(result, CollectorTimeoutError)
                else None,
                "timeout_seconds": spec.timeout_seconds,
            }
            utils.verbose_log(f"Collector failed: {spec.name}: {error_message}")
            collected[spec.name] = spec.default
        else:
            value, duration_ms = result
            collection_status[spec.name] = {
                "status": "ok",
                "error": None,
                "duration_ms": round(duration_ms, 3),
                "timeout_seconds": spec.timeout_seconds,
            }
            collected[spec.name] = value

    return collected, collection_errors, collection_status


async def run_collector(spec: CollectorSpec) -> tuple[object, float]:
    """Execute one collector with its configured timeout."""
    started = time.perf_counter()
    try:
        result = await asyncio.wait_for(spec.run(), timeout=spec.timeout_seconds)
    except TimeoutError as exc:
        duration_ms = (time.perf_counter() - started) * 1000
        raise CollectorTimeoutError(
            f"collector exceeded {spec.timeout_seconds:g}s timeout",
            duration_ms,
        ) from exc
    return result, (time.perf_counter() - started) * 1000
