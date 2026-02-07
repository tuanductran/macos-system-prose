# Async Migration Example

This document shows how to convert synchronous collectors to use the new async infrastructure.

## Current Implementation (Using asyncio.to_thread)

The current implementation in `engine.py` uses `asyncio.to_thread()` to run synchronous collectors in parallel:

```python
results = await asyncio.gather(
    asyncio.to_thread(collect_system_info),
    asyncio.to_thread(collect_hardware_info),
    # ... other collectors
    return_exceptions=True,
)
```

This approach:
- ✅ **Works immediately** with existing synchronous collectors
- ✅ **Achieves true parallelism** via thread pool
- ✅ **Minimal code changes** required
- ⚠️ Still uses `subprocess.run()` which blocks threads

## Future Optimization (Pure Async)

For even better performance, collectors can be converted to use `async_run_command()` directly:

### Example: Converting `collect_system_info()` to Async

**Before (Synchronous):**
```python
def collect_system_info() -> SystemInfo:
    log("Collecting system information...")
    
    version = run(["sw_vers", "-productVersion"])
    kernel = run(["uname", "-r"])
    architecture = platform.machine()
    uptime = run(["uptime"])
    
    return {
        "os": "Darwin",
        "macos_version": version,
        "kernel": kernel,
        "architecture": architecture,
        "uptime": _parse_uptime(uptime),
        # ... more fields
    }
```

**After (Async):**
```python
async def collect_system_info() -> SystemInfo:
    log("Collecting system information...")
    
    # Run commands concurrently using asyncio.gather
    version, kernel, uptime_raw = await asyncio.gather(
        async_run_command(["sw_vers", "-productVersion"]),
        async_run_command(["uname", "-r"]),
        async_run_command(["uptime"]),
    )
    
    # Non-blocking operations
    architecture = platform.machine()
    
    return {
        "os": "Darwin",
        "macos_version": version,
        "kernel": kernel,
        "architecture": architecture,
        "uptime": _parse_uptime(uptime_raw),
        # ... more fields
    }
```

**Benefits of Pure Async:**
- Multiple commands run concurrently within a single collector
- No thread overhead
- Better CPU utilization
- Easier to debug and reason about

### Migration Steps

1. **Change function signature:** `def` → `async def`
2. **Replace `run()` calls:** Use `await async_run_command()`
3. **Replace `get_json_output()` calls:** Use `await async_get_json_output()`
4. **Group concurrent commands:** Use `asyncio.gather()` for independent operations
5. **Update engine.py:** Remove `asyncio.to_thread()` wrapper for converted collectors

### Example: Concurrent Commands Within a Collector

```python
async def collect_hardware_info() -> HardwareInfo:
    log("Collecting hardware information...")
    
    # These commands are independent and can run concurrently
    cpu_info, memory_info, gpu_info = await asyncio.gather(
        async_run_command(["sysctl", "-n", "machdep.cpu.brand_string"]),
        async_run_command(["sysctl", "-n", "hw.memsize"]),
        async_run_command(["system_profiler", "SPDisplaysDataType"]),
    )
    
    return {
        "cpu": cpu_info,
        "memory_gb": int(memory_info) / (1024**3) if memory_info else None,
        # ... parse gpu_info
    }
```

## Migration Priority

Collectors with the most subprocess calls benefit most from async conversion:

1. **High Priority:**
   - `collect_system_info()` - 10+ subprocess calls
   - `collect_hardware_info()` - 8+ subprocess calls
   - `collect_developer_tools()` - 20+ subprocess calls

2. **Medium Priority:**
   - `collect_network_info()` - 5+ subprocess calls
   - `collect_packages()` - 7+ subprocess calls

3. **Low Priority:**
   - Collectors with 1-2 subprocess calls
   - Collectors with complex dependencies

## Current Status

✅ **Phase 1 Complete:** Async infrastructure added
- `async_run_command()` and `async_get_json_output()` in `utils.py`
- `collect_all()` uses `asyncio.gather()` with `asyncio.to_thread()`
- All collectors run in parallel via thread pool
- Tests added and passing
- Type hints complete
- Backward compatible

🔄 **Phase 2 (Optional):** Convert collectors to pure async
- Choose collectors based on priority
- Convert one at a time
- Maintain backward compatibility
- Benchmark performance improvements
