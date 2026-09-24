# Documentation Directory

Technical documentation for the `macos-system-prose` project.

---

## 📖 Available Documentation

| Document | Size | Purpose |
|----------|------|---------|
| **[apple-oss-analysis.md](./apple-oss-analysis.md)** | 13 KB | Apple OSS analysis |
| **[xnu-quick-reference.md](./xnu-quick-reference.md)** | Reference | XNU kernel reference |
| **[oclp-reference.md](./oclp-reference.md)** | Reference | OpenCore Legacy Patcher compatibility and evidence reference |
| **[platform-compatibility.md](./platform-compatibility.md)** | Reference | Intel/Apple-silicon CI contract and known limitations |

---

## 📚 Related Documentation

- **[../README.md](../README.md)** (17 KB) - User documentation
- **[../AGENTS.md](../AGENTS.md)** (33 KB) - AI agent instructions
- **[../LICENSE](../LICENSE)** - MIT License

---

## 📊 Project Status

| Metric | Value | Status |
|--------|-------|--------|
| **Test Collection** | 130 tests (latest validated CI run) | ℹ️ |
| **Ruff / MyPy** | Enforced by CI | ℹ️ |
| **Architecture CI** | Apple silicon + explicit Intel smoke test | ℹ️ |
| **Project Phase** | v1.4 platform compatibility hardening | ✅ |

---

**Last Updated:** 2026-09-24  
**Status:** Reference documentation; v1.4 hardening is complete and validation status is reported by CI


## Reference freshness

The Apple and OCLP references in this directory are reviewed against their upstream sources rather than treated as immutable facts. The current review date is **2026-09-24**.

- Apple OSS references: see [apple-oss-analysis.md](./apple-oss-analysis.md).
- XNU reference: see [xnu-quick-reference.md](./xnu-quick-reference.md).
- OCLP reference: see [oclp-reference.md](./oclp-reference.md).
- Machine-readable OCLP knowledge is maintained in [../data/oclp_knowledge.json](../data/oclp_knowledge.json) with an explicit `checked_at` date.
