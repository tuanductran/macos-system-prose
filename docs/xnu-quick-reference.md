# XNU Kernel Quick Reference for macos-system-prose

**Quick guide for using XNU source code to improve our system introspection**

Repository: https://github.com/apple-oss-distributions/xnu  
Purpose: Reference documentation for understanding macOS internals  
Usage: Study headers, validate parsing, discover data sources

## What is XNU?

**XNU** = **X is Not Unix**

Hybrid kernel architecture combining:
- **Mach** - Microkernel (IPC, threads, VM)
- **BSD** - UNIX layer (processes, networking, FS)
- **IOKit** - Device driver framework (C++)

## Priority Files for Our Project

### 1. sysctl Definitions (HIGHEST PRIORITY)

**Files:**
```text
xnu/bsd/sys/sysctl.h          # sysctl(3) definitions
xnu/bsd/kern/kern_sysctl.c    # sysctl implementation
```

**What We Collect:**
```python
# Current: We run sysctl -a and parse output
# XNU shows: Exact data types, meanings, valid ranges
```

**sysctl Categories We Use:**
- kern.* - Kernel info (osversion, hostname, boottime)
- hw.* - Hardware (memsize, cpufrequency, ncpu)
- machdep.cpu.* - CPU details (brand, features, family)
- vm.* - Virtual memory statistics
- net.* - Network interfaces

**Study These:**
```bash
# Clone XNU
git clone https://github.com/apple-oss-distributions/xnu.git
cd xnu

# Find all sysctl definitions
grep -r "SYSCTL_NODE" bsd/kern/
grep -r "hw\." bsd/kern/

# CPU info
cat bsd/kern/kern_mib.c
```

### 2. IOKit Property Keys

**Files:**
```text
xnu/iokit/IOKit/IOKitKeys.h   # Standard property key definitions
xnu/iokit/IOKit/IORegistryEntry.h  # IORegistry structure
```

**What We Collect:**
```python
# Current: Parse ioreg -l output
# XNU shows: Official property key names and meanings
```

**Key Properties We Use:**
- IOClass - Driver class name
- model - Device model string
- vendor-id, device-id - PCI identifiers

### 3. Process Information

**Files:**
```text
xnu/bsd/sys/proc.h            # Process structures
xnu/bsd/kern/kern_proc.c      # Process management
```

**What We Collect:**
```python
# Current: Parse ps aux output
# XNU shows: Process states, flags, relationships
```

### 4. Security & SIP

**Files:**
```text
xnu/security/mac/             # Mandatory Access Control
```

**What We Collect:**
```python
# Current: Parse csrutil status output
# XNU shows: SIP flag definitions and meanings
```

## Practical Examples

### Example 1: Understanding sysctl Output

**Current Code:**
```python
# We run: sysctl hw.memsize
# Output: hw.memsize: 17179869184
# We parse: int(output.split(": ")[1])
```

**After Studying XNU:**
```c
// xnu/bsd/kern/kern_mib.c
SYSCTL_QUAD(_hw, HW_MEMSIZE, memsize, CTLFLAG_RD, &max_mem, "");
```

**Understanding:**
- Type is QUAD (64-bit integer)
- Flags are RD (read-only)
- Value is in bytes (not KB, MB, GB)

### Example 2: IORegistry Properties

**Current Code:**
```python
# We parse ioreg output for display info
# Property: "DisplayProductID" = 42210
```

**After Studying XNU:**
```objective-c
// iokit/IOKit/graphics/IODisplay.h
#define kDisplayProductIDKey "DisplayProductID"
```

**Understanding:**
- Official key names defined in headers
- Data types are specified

## How XNU Helps Our Project

### 1. Validation
- ✅ Verify our parsing matches kernel reality
- ✅ Check data types are correct
- ✅ Understand flag meanings

### 2. Discovery
- ✅ Find new sysctl variables to collect
- ✅ Discover IOKit properties we are missing
- ✅ Learn about undocumented features

### 3. Documentation
- ✅ Document why certain values exist
- ✅ Explain flag combinations
- ✅ Add accurate comments to our code

### 4. Accuracy
- ✅ Parse numbers correctly (bytes vs KB)
- ✅ Handle edge cases kernel handles
- ✅ Understand error conditions

## Action Items for macos-system-prose

### Phase 1: Study (Current)
- [ ] Clone XNU repository locally
- [ ] Read bsd/sys/sysctl.h for all sysctl definitions
- [ ] Read iokit/IOKit/IOKitKeys.h for IOKit properties
- [ ] Document findings in code comments

### Phase 2: Validate (Next)
- [ ] Compare our sysctl parsing with kernel definitions
- [ ] Verify IOKit property names we use are official
- [ ] Check data types match kernel expectations
- [ ] Add type safety based on kernel types

### Phase 3: Enhance (Future)
- [ ] Add missing sysctl variables we discover
- [ ] Improve IOKit parsing with new properties
- [ ] Better error handling based on kernel behavior
- [ ] Document edge cases from kernel source

## Important Notes

**DO:**
- ✅ Study XNU headers as documentation
- ✅ Validate our command-line parsing
- ✅ Learn about data structures
- ✅ Discover new data sources

**DO NOT:**
- ❌ Try to link against kernel
- ❌ Add native code dependencies
- ❌ Use kernel APIs directly
- ❌ Break zero-dependency policy

**Remember:**
XNU is **REFERENCE DOCUMENTATION** only, not for direct integration!

## Quick Commands

```bash
# Clone XNU
git clone https://github.com/apple-oss-distributions/xnu.git

# Find sysctl definitions
cd xnu
grep -r "SYSCTL_" bsd/kern/ | grep -i "kern\."

# Find IOKit keys
cat iokit/IOKit/IOKitKeys.h

# Find security definitions
find security/ -name "*.h"

# Search for specific terms
grep -ri "system integrity" .
```

## Resources

- **XNU Repository**: https://github.com/apple-oss-distributions/xnu
- **Apple Open Source**: https://opensource.apple.com/
- **Darwin Documentation**: https://developer.apple.com/library/archive/documentation/Darwin/
- **IOKit Fundamentals**: https://developer.apple.com/library/archive/documentation/DeviceDrivers/Conceptual/IOKitFundamentals/

---

**Last Updated**: 2026-02-08  
**Status**: Active reference for development
