# Examples

This directory contains example scripts and demos for macos-system-prose.

## TUI Demo

**`tui_demo.py`** - Interactive Terminal UI demonstration with mock data.

Launch the TUI without running a full system scan:

```bash
python3 examples/tui_demo.py
```

This demo uses synthetic data to showcase the TUI's features:

- Monitor dashboard with system metrics
- Process manager with real-time updates
- Security status overview
- Network interface information
- Developer tools detection

Press `q` to quit, `r` to refresh.

## Notes

These are manual demonstration scripts, not automated tests. For automated testing, see the `tests/` directory.


## Machine profile fixtures

Three synthetic machine profiles are provided: `intel-oclp`, `intel-native`, and `apple-silicon`. Each includes Python, Node.js, Bun, pnpm, npm, Yarn, Xcode, xcode-select, Swift, Go, Rust, Docker, Homebrew, version managers, editor, terminal and shell tooling. Homebrew uses the documented default prefixes `/usr/local` for Intel and `/opt/homebrew` for Apple Silicon. Xcode and Command Line Tools are represented separately via Xcode version and `xcode-select` developer directory. OCLP is represented as explicit evidence rather than as an inferred security state.

All values are synthetic and illustrative; never put real hostnames, email addresses, IP/MAC addresses, NVRAM values, tokens, or credentials into examples.
