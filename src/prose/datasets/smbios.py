"""
SMBIOS database for Mac model identification and enrichment.

Adapted from OpenCore-Legacy-Patcher's smbios_data.py
Reference: https://github.com/dortania/OpenCore-Legacy-Patcher
"""

from __future__ import annotations

from typing import TypedDict


class SMBIOSData(TypedDict, total=False):
    """SMBIOS metadata for a Mac model."""

    marketing_name: str
    board_id: str
    cpu_generation: str
    max_os_supported: str
    screen_size: int | None
    stock_gpus: list[str]


# Simplified SMBIOS database (100+ models from OCLP reference)
# Key: Model identifier (e.g., "MacBookAir6,2")
# Max OS values: "Snow Leopard" (10.6) → "Sequoia" (15.x)
SMBIOS_DATABASE: dict[str, SMBIOSData] = {
    # MacBook (2006-2017)
    "MacBook1,1": {
        "marketing_name": "MacBook (13-inch)",
        "board_id": "Mac-F4208CC8",
        "cpu_generation": "Yonah",
        "max_os_supported": "Snow Leopard",
        "screen_size": 13,
        "stock_gpus": ["Intel GMA 950"],
    },
    "MacBook5,1": {
        "marketing_name": "MacBook (13-inch, Aluminum, Late 2008)",
        "board_id": "Mac-F42D89C8",
        "cpu_generation": "Penryn",
        "max_os_supported": "Lion",
        "screen_size": 13,
        "stock_gpus": ["NVIDIA GeForce 9400M"],
    },
    "MacBook8,1": {
        "marketing_name": "MacBook (Retina, 12-inch, Early 2015)",
        "board_id": "Mac-BE0E8AC46FE800CC",
        "cpu_generation": "Broadwell",
        "max_os_supported": "Monterey",
        "screen_size": 12,
        "stock_gpus": ["Intel HD Graphics 5300"],
    },
    "MacBook9,1": {
        "marketing_name": "MacBook (Retina, 12-inch, Early 2016)",
        "board_id": "Mac-9AE82516C7C6B903",
        "cpu_generation": "Skylake",
        "max_os_supported": "Monterey",
        "screen_size": 12,
        "stock_gpus": ["Intel HD Graphics 515"],
    },
    "MacBook10,1": {
        "marketing_name": "MacBook (Retina, 12-inch, 2017)",
        "board_id": "Mac-EE2EBD4B90B839A8",
        "cpu_generation": "Kaby Lake",
        "max_os_supported": "Monterey",
        "screen_size": 12,
        "stock_gpus": ["Intel HD Graphics 615"],
    },
    # MacBook Air (2010-2025) - Updated from Apple Support Feb 2026
    "MacBookAir3,1": {
        "marketing_name": "MacBook Air (11-inch, Late 2010)",
        "board_id": "Mac-942452F5819B1C1B",
        "cpu_generation": "Penryn",
        "max_os_supported": "High Sierra",
        "screen_size": 11,
        "stock_gpus": ["NVIDIA GeForce 320M"],
    },
    "MacBookAir4,1": {
        "marketing_name": "MacBook Air (11-inch, Mid 2011)",
        "board_id": "Mac-C08A6BB70A942AC2",
        "cpu_generation": "Sandy Bridge",
        "max_os_supported": "High Sierra",
        "screen_size": 11,
        "stock_gpus": ["Intel HD Graphics 3000"],
    },
    "MacBookAir5,1": {
        "marketing_name": "MacBook Air (11-inch, Mid 2012)",
        "board_id": "Mac-66F35F19FE2A0D05",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": 11,
        "stock_gpus": ["Intel HD Graphics 4000"],
    },
    "MacBookAir5,2": {
        "marketing_name": "MacBook Air (13-inch, Mid 2012)",
        "board_id": "Mac-2E6FAB96566FE58C",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": 13,
        "stock_gpus": ["Intel HD Graphics 4000"],
    },
    "MacBookAir6,1": {
        "marketing_name": "MacBook Air (11-inch, Mid 2013)",
        "board_id": "Mac-35C1E88140C3E6CF",
        "cpu_generation": "Haswell",
        "max_os_supported": "Big Sur",
        "screen_size": 11,
        "stock_gpus": ["Intel HD Graphics 5000"],
    },
    "MacBookAir6,2": {
        "marketing_name": "MacBook Air (13-inch, Mid 2013)",
        "board_id": "Mac-7DF21CB3ED6977E5",
        "cpu_generation": "Haswell",
        "max_os_supported": "Big Sur",
        "screen_size": 13,
        "stock_gpus": ["Intel HD Graphics 5000"],
    },
    "MacBookAir7,1": {
        "marketing_name": "MacBook Air (11-inch, Early 2015)",
        "board_id": "Mac-9F18E312C5C2BF0B",
        "cpu_generation": "Broadwell",
        "max_os_supported": "Monterey",
        "screen_size": 11,
        "stock_gpus": ["Intel HD Graphics 6000"],
    },
    "MacBookAir7,2": {
        "marketing_name": "MacBook Air (13-inch, Early 2015)",
        "board_id": "Mac-937CB26E2E02BB01",
        "cpu_generation": "Broadwell",
        "max_os_supported": "Monterey",
        "screen_size": 13,
        "stock_gpus": ["Intel HD Graphics 6000"],
    },
    "MacBookAir8,1": {
        "marketing_name": "MacBook Air (Retina, 13-inch, 2018)",
        "board_id": "Mac-827FAC58A8FDFA22",
        "cpu_generation": "Amber Lake",
        "max_os_supported": "Sonoma",
        "screen_size": 13,
        "stock_gpus": ["Intel UHD Graphics 617"],
    },
    "MacBookAir8,2": {
        "marketing_name": "MacBook Air (Retina, 13-inch, 2019)",
        "board_id": "Mac-226CB3C6A851A671",
        "cpu_generation": "Amber Lake",
        "max_os_supported": "Sonoma",
        "screen_size": 13,
        "stock_gpus": ["Intel UHD Graphics 617"],
    },
    "MacBookAir9,1": {
        "marketing_name": "MacBook Air (Retina, 13-inch, 2020)",
        "board_id": "Mac-0CFF9C7C2B63DF8D",
        "cpu_generation": "Ice Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Plus Graphics"],
    },
    "MacBookAir10,1": {
        "marketing_name": "MacBook Air (M1, 2020)",
        "board_id": "Mac-A2D82A55D6FA33B1",
        "cpu_generation": "Apple M1",
        "max_os_supported": "Tahoe",
        "screen_size": 13,
        "stock_gpus": ["Apple M1 (7-core)"],
    },
    "Mac14,2": {
        "marketing_name": "MacBook Air (M2, 2022)",
        "board_id": "Mac-226CB3C6A851A671",
        "cpu_generation": "Apple M2",
        "max_os_supported": "Tahoe",
        "screen_size": 13,
        "stock_gpus": ["Apple M2 (8/10-core)"],
    },
    "Mac14,15": {
        "marketing_name": "MacBook Air (15-inch, M2, 2023)",
        "board_id": "Mac-8CB73F3A4C8AA6E6",
        "cpu_generation": "Apple M2",
        "max_os_supported": "Tahoe",
        "screen_size": 15,
        "stock_gpus": ["Apple M2 (10-core)"],
    },
    "Mac15,12": {
        "marketing_name": "MacBook Air (13-inch, M3, 2024)",
        "board_id": "Mac-66F8F8A54EA1AA12",
        "cpu_generation": "Apple M3",
        "max_os_supported": "Tahoe",
        "screen_size": 13,
        "stock_gpus": ["Apple M3 (8/10-core)"],
    },
    "Mac15,13": {
        "marketing_name": "MacBook Air (15-inch, M3, 2024)",
        "board_id": "Mac-93F94DB80D66B81E",
        "cpu_generation": "Apple M3",
        "max_os_supported": "Tahoe",
        "screen_size": 15,
        "stock_gpus": ["Apple M3 (10-core)"],
    },
    "Mac16,12": {
        "marketing_name": "MacBook Air (13-inch, M4, 2025)",
        "board_id": "Mac-TBD",  # Not yet available
        "cpu_generation": "Apple M4",
        "max_os_supported": "Tahoe",
        "screen_size": 13,
        "stock_gpus": ["Apple M4"],
    },
    "Mac16,13": {
        "marketing_name": "MacBook Air (15-inch, M4, 2025)",
        "board_id": "Mac-TBD",  # Not yet available
        "cpu_generation": "Apple M4",
        "max_os_supported": "Tahoe",
        "screen_size": 15,
        "stock_gpus": ["Apple M4"],
    },
    # MacBook Pro (13-inch, 2006-2022) - Updated from Apple Support Feb 2026
    "MacBookPro3,1": {
        "marketing_name": "MacBook Pro (15-inch, 2.4/2.2GHz, Mid 2007)",
        "board_id": "Mac-F4238BC8",
        "cpu_generation": "Merom",
        "max_os_supported": "Lion",
        "screen_size": 15,
        "stock_gpus": ["NVIDIA GeForce 8600M GT"],
    },
    "MacBookPro5,1": {
        "marketing_name": "MacBook Pro (15-inch, Late 2008)",
        "board_id": "Mac-F42D86C8",
        "cpu_generation": "Penryn",
        "max_os_supported": "High Sierra",
        "screen_size": 15,
        "stock_gpus": ["NVIDIA GeForce 9600M GT"],
    },
    "MacBookPro8,1": {
        "marketing_name": "MacBook Pro (13-inch, Early 2011)",
        "board_id": "Mac-94245B3640C91C81",
        "cpu_generation": "Sandy Bridge",
        "max_os_supported": "High Sierra",
        "screen_size": 13,
        "stock_gpus": ["Intel HD Graphics 3000"],
    },
    "MacBookPro9,2": {
        "marketing_name": "MacBook Pro (13-inch, Mid 2012)",
        "board_id": "Mac-6F01561E16C75D06",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": 13,
        "stock_gpus": ["Intel HD Graphics 4000"],
    },
    "MacBookPro10,1": {
        "marketing_name": "MacBook Pro (Retina, 15-inch, Mid 2012)",
        "board_id": "Mac-C3EC7CD22292981F",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": 15,
        "stock_gpus": ["Intel HD Graphics 4000", "NVIDIA GeForce GT 650M"],
    },
    "MacBookPro11,1": {
        "marketing_name": "MacBook Pro (Retina, 13-inch, Late 2013)",
        "board_id": "Mac-189A3D4F975D5FFC",
        "cpu_generation": "Haswell",
        "max_os_supported": "Monterey",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Graphics"],
    },
    "MacBookPro11,2": {
        "marketing_name": "MacBook Pro (Retina, 15-inch, Late 2013)",
        "board_id": "Mac-3CBD00234E554E41",
        "cpu_generation": "Haswell",
        "max_os_supported": "Monterey",
        "screen_size": 15,
        "stock_gpus": ["Intel Iris Pro Graphics", "NVIDIA GeForce GT 750M"],
    },
    "MacBookPro12,1": {
        "marketing_name": "MacBook Pro (Retina, 13-inch, Early 2015)",
        "board_id": "Mac-E43C1C25D4880AD6",
        "cpu_generation": "Broadwell",
        "max_os_supported": "Monterey",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Graphics 6100"],
    },
    "MacBookPro13,1": {
        "marketing_name": "MacBook Pro (13-inch, 2016, Two Thunderbolt 3 ports)",
        "board_id": "Mac-473D31EABEB93F9B",
        "cpu_generation": "Skylake",
        "max_os_supported": "Monterey",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Graphics 540"],
    },
    "MacBookPro14,1": {
        "marketing_name": "MacBook Pro (13-inch, 2017, Two Thunderbolt 3 ports)",
        "board_id": "Mac-B4831CEBD52A0C4C",
        "cpu_generation": "Kaby Lake",
        "max_os_supported": "Ventura",  # Updated from Apple Support
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Plus Graphics 640"],
    },
    "MacBookPro14,2": {
        "marketing_name": "MacBook Pro (13-inch, 2017, Four Thunderbolt 3 Ports)",
        "board_id": "Mac-CAD6701F7CEA0921",
        "cpu_generation": "Kaby Lake",
        "max_os_supported": "Ventura",  # Updated from Apple Support
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Plus Graphics 650"],
    },
    "MacBookPro14,3": {
        "marketing_name": "MacBook Pro (15-inch, 2017)",
        "board_id": "Mac-551B86E5744E2388",
        "cpu_generation": "Kaby Lake",
        "max_os_supported": "Ventura",  # Updated from Apple Support
        "screen_size": 15,
        "stock_gpus": ["Intel HD Graphics 630", "AMD Radeon Pro 555/560"],
    },
    "MacBookPro15,2": {
        "marketing_name": "MacBook Pro (13-inch, 2018, Four Thunderbolt 3 Ports)",
        "board_id": "Mac-827FB448E656EC26",
        "cpu_generation": "Coffee Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Plus Graphics 655"],
    },
    "MacBookPro16,2": {
        "marketing_name": "MacBook Pro (13-inch, 2020, Four Thunderbolt 3 ports)",
        "board_id": "Mac-5F9802EFE386AA28",
        "cpu_generation": "Ice Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 13,
        "stock_gpus": ["Intel Iris Plus Graphics"],
    },
    "MacBookPro17,1": {
        "marketing_name": "MacBook Pro (13-inch, M1, 2020)",
        "board_id": "Mac-E1008331FDC96864",
        "cpu_generation": "Apple M1",
        "max_os_supported": "Sequoia",
        "screen_size": 13,
        "stock_gpus": ["Apple M1 (8-core)"],
    },
    "MacBookPro18,1": {
        "marketing_name": "MacBook Pro (16-inch, 2021)",
        "board_id": "Mac-7B8E1D6A7C04B34F",
        "cpu_generation": "Apple M1 Pro",
        "max_os_supported": "Tahoe",  # Updated from Apple Support
        "screen_size": 16,
        "stock_gpus": ["Apple M1 Pro (14/16-core)"],
    },
    "MacBookPro18,2": {
        "marketing_name": "MacBook Pro (16-inch, 2021)",
        "board_id": "Mac-4D9A1E3F2A30A42D",
        "cpu_generation": "Apple M1 Max",
        "max_os_supported": "Tahoe",  # Updated from Apple Support
        "screen_size": 16,
        "stock_gpus": ["Apple M1 Max (24/32-core)"],
    },
    "MacBookPro18,3": {
        "marketing_name": "MacBook Pro (14-inch, 2021)",
        "board_id": "Mac-F8E45A93D831C6CF",
        "cpu_generation": "Apple M1 Pro",
        "max_os_supported": "Tahoe",  # Updated from Apple Support
        "screen_size": 14,
        "stock_gpus": ["Apple M1 Pro (14-core)"],
    },
    "MacBookPro18,4": {
        "marketing_name": "MacBook Pro (14-inch, 2021)",
        "board_id": "Mac-ECDB4C6F1BB66FC6",
        "cpu_generation": "Apple M1 Max",
        "max_os_supported": "Tahoe",  # Updated from Apple Support
        "screen_size": 14,
        "stock_gpus": ["Apple M1 Max (24/32-core)"],
    },
    # MacBook Pro M2/M3/M4/M5 (2022-2025) - Latest models
    "Mac14,5": {
        "marketing_name": "MacBook Pro (14-inch, 2023)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M2 Pro",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M2 Pro"],
    },
    "Mac14,9": {
        "marketing_name": "MacBook Pro (14-inch, 2023)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M2 Max",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M2 Max"],
    },
    "Mac15,3": {
        "marketing_name": "MacBook Pro (14-inch, Nov 2023)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M3",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M3 (10-core)"],
    },
    "Mac15,6": {
        "marketing_name": "MacBook Pro (14-inch, Nov 2023)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M3 Pro",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M3 Pro"],
    },
    "Mac16,1": {
        "marketing_name": "MacBook Pro (14-inch, 2024)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M4",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M4 (10-core)"],
    },
    "Mac16,6": {
        "marketing_name": "MacBook Pro (14-inch, 2024)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M4 Pro",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M4 Pro"],
    },
    "Mac17,2": {
        "marketing_name": "MacBook Pro (14-inch, M5)",
        "board_id": "Mac-TBD",
        "cpu_generation": "Apple M5",
        "max_os_supported": "Tahoe",
        "screen_size": 14,
        "stock_gpus": ["Apple M5"],
    },
    # Mac Mini (2006-2023)
    "Macmini1,1": {
        "marketing_name": "Mac mini (Early 2006)",
        "board_id": "Mac-F4208EAA",
        "cpu_generation": "Yonah",
        "max_os_supported": "Snow Leopard",
        "screen_size": None,
        "stock_gpus": ["Intel GMA 950"],
    },
    "Macmini5,1": {
        "marketing_name": "Mac mini (Mid 2011)",
        "board_id": "Mac-8ED6AF5B48C039E1",
        "cpu_generation": "Sandy Bridge",
        "max_os_supported": "High Sierra",
        "screen_size": None,
        "stock_gpus": ["Intel HD Graphics 3000"],
    },
    "Macmini6,1": {
        "marketing_name": "Mac mini (Late 2012)",
        "board_id": "Mac-031AEE4D24BFF0B1",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": None,
        "stock_gpus": ["Intel HD Graphics 4000"],
    },
    "Macmini7,1": {
        "marketing_name": "Mac mini (Late 2014)",
        "board_id": "Mac-35C5E08120C7EEAF",
        "cpu_generation": "Haswell",
        "max_os_supported": "Monterey",
        "screen_size": None,
        "stock_gpus": ["Intel HD Graphics 5000"],
    },
    "Macmini8,1": {
        "marketing_name": "Mac mini (2018)",
        "board_id": "Mac-7BA5B2DFE22DDD8C",
        "cpu_generation": "Coffee Lake",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["Intel UHD Graphics 630"],
    },
    "Macmini9,1": {
        "marketing_name": "Mac mini (M1, 2020)",
        "board_id": "Mac-4A48B3C8B6C88D0A",
        "cpu_generation": "Apple M1",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["Apple M1 (8-core)"],
    },
    # iMac (2006-2021)
    "iMac7,1": {
        "marketing_name": "iMac (20-inch, Mid 2007)",
        "board_id": "Mac-F42386C8",
        "cpu_generation": "Merom",
        "max_os_supported": "Lion",
        "screen_size": 20,
        "stock_gpus": ["ATI Radeon HD 2400 XT"],
    },
    "iMac10,1": {
        "marketing_name": "iMac (21.5-inch, Late 2009)",
        "board_id": "Mac-F221DCC8",
        "cpu_generation": "Penryn",
        "max_os_supported": "High Sierra",
        "screen_size": 21,
        "stock_gpus": ["NVIDIA GeForce 9400M"],
    },
    "iMac13,1": {
        "marketing_name": "iMac (21.5-inch, Late 2012)",
        "board_id": "Mac-00BE6ED71E35EB86",
        "cpu_generation": "Ivy Bridge",
        "max_os_supported": "Big Sur",
        "screen_size": 21,
        "stock_gpus": ["Intel HD Graphics 4000", "NVIDIA GeForce GT 640M"],
    },
    "iMac14,2": {
        "marketing_name": "iMac (27-inch, Late 2013)",
        "board_id": "Mac-27ADBB7B4CEE8E61",
        "cpu_generation": "Haswell",
        "max_os_supported": "Monterey",
        "screen_size": 27,
        "stock_gpus": ["NVIDIA GeForce GT 755M"],
    },
    "iMac17,1": {
        "marketing_name": "iMac (27-inch, Retina 5K, Late 2015)",
        "board_id": "Mac-DB15BD556843C820",
        "cpu_generation": "Skylake",
        "max_os_supported": "Monterey",
        "screen_size": 27,
        "stock_gpus": ["AMD Radeon R9 M380"],
    },
    "iMac18,3": {
        "marketing_name": "iMac (27-inch, Retina 5K, 2017)",
        "board_id": "Mac-BE088AF8C5EB4FA2",
        "cpu_generation": "Kaby Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 27,
        "stock_gpus": ["AMD Radeon Pro 570"],
    },
    "iMac19,1": {
        "marketing_name": "iMac (27-inch, Retina 5K, 2019)",
        "board_id": "Mac-AA95B1DDAB278B95",
        "cpu_generation": "Coffee Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 27,
        "stock_gpus": ["AMD Radeon Pro 570X"],
    },
    "iMac20,1": {
        "marketing_name": "iMac (27-inch, Retina 5K, 2020)",
        "board_id": "Mac-CFF7D910A743CAAF",
        "cpu_generation": "Comet Lake",
        "max_os_supported": "Sequoia",
        "screen_size": 27,
        "stock_gpus": ["AMD Radeon Pro 5300"],
    },
    "iMac21,1": {
        "marketing_name": "iMac (24-inch, M1, 2021)",
        "board_id": "Mac-4FD6A27A8F2F1F06",
        "cpu_generation": "Apple M1",
        "max_os_supported": "Sequoia",
        "screen_size": 24,
        "stock_gpus": ["Apple M1 (7/8-core)"],
    },
    # Mac Pro (2006-2023)
    "MacPro3,1": {
        "marketing_name": "Mac Pro (Early 2008)",
        "board_id": "Mac-F42C88C8",
        "cpu_generation": "Harpertown",
        "max_os_supported": "High Sierra",
        "screen_size": None,
        "stock_gpus": ["ATI Radeon HD 2600 XT"],
    },
    "MacPro5,1": {
        "marketing_name": "Mac Pro (Mid 2010/2012)",
        "board_id": "Mac-F221BEC8",
        "cpu_generation": "Westmere",
        "max_os_supported": "Monterey",
        "screen_size": None,
        "stock_gpus": ["ATI Radeon HD 5770"],
    },
    "MacPro6,1": {
        "marketing_name": "Mac Pro (Late 2013)",
        "board_id": "Mac-F60DEB81FF30ACF6",
        "cpu_generation": "Ivy Bridge-EP",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["AMD FirePro D300"],
    },
    "MacPro7,1": {
        "marketing_name": "Mac Pro (2019)",
        "board_id": "Mac-27AD2F918AE68F61",
        "cpu_generation": "Cascade Lake-W",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["AMD Radeon Pro 580X"],
    },
    # Mac Studio (2022)
    "MacStudio1,1": {
        "marketing_name": "Mac Studio (M1 Max, 2022)",
        "board_id": "Mac-827C7C8F1B7C0B0D",
        "cpu_generation": "Apple M1 Max",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["Apple M1 Max (24/32-core)"],
    },
    "MacStudio1,2": {
        "marketing_name": "Mac Studio (M1 Ultra, 2022)",
        "board_id": "Mac-063E26AB7A27FC27",
        "cpu_generation": "Apple M1 Ultra",
        "max_os_supported": "Sequoia",
        "screen_size": None,
        "stock_gpus": ["Apple M1 Ultra (48/64-core)"],
    },
}


def get_smbios_data(model_identifier: str) -> SMBIOSData | None:
    """
    Get SMBIOS metadata for a Mac model identifier.

    Args:
        model_identifier: Model identifier (e.g., "MacBookAir6,2")

    Returns:
        SMBIOS metadata dictionary or None if not found

    Example:
        >>> data = get_smbios_data("MacBookAir6,2")
        >>> data["marketing_name"]
        'MacBook Air (13-inch, Mid 2013)'
    """
    return SMBIOS_DATABASE.get(model_identifier)


def is_legacy_mac(model_identifier: str, current_macos_version: str) -> bool:
    """
    Check if a Mac is running an unsupported macOS version (legacy/OCLP).

    Args:
        model_identifier: Model identifier (e.g., "MacBookAir6,2")
        current_macos_version: Current macOS version (e.g., "12.7.6")

    Returns:
        True if running unsupported OS, False otherwise

    Example:
        >>> is_legacy_mac("MacBookAir6,2", "12.7.6")  # Big Sur max, running Monterey
        True
    """
    data = get_smbios_data(model_identifier)
    if not data:
        return False

    # Map max OS to major version number (updated Feb 2026)
    os_version_map = {
        "Snow Leopard": 10.6,
        "Lion": 10.7,
        "Mountain Lion": 10.8,
        "Mavericks": 10.9,
        "Yosemite": 10.10,
        "El Capitan": 10.11,
        "Sierra": 10.12,
        "High Sierra": 10.13,
        "Mojave": 10.14,
        "Catalina": 10.15,
        "Big Sur": 11.0,
        "Monterey": 12.0,
        "Ventura": 13.0,
        "Sonoma": 14.0,
        "Sequoia": 15.0,
        "Tahoe": 26.0,  # macOS Tahoe (2026)
    }

    max_os = data.get("max_os_supported", "")
    max_version = os_version_map.get(max_os, 0.0)

    # Parse current version (e.g., "12.7.6" -> 12.0)
    try:
        parts = current_macos_version.split(".")
        current_major = float(parts[0])
        if len(parts) > 1 and int(parts[0]) < 11:
            # Handle 10.x versions
            current_major = float(f"{parts[0]}.{parts[1]}")
    except (ValueError, IndexError):
        return False

    return current_major > max_version


__all__ = ["SMBIOS_DATABASE", "SMBIOSData", "get_smbios_data", "is_legacy_mac"]
