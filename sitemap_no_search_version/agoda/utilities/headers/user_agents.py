# agoda/utilities/headers/user_agents.py

"""
User-Agent rotator and Chrome version-specific x-client-data mapping.
"""

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME]
os_list = [OperatingSystem.WINDOWS, OperatingSystem.MAC]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=os_list, limit=100)

CACHED_USER_AGENTS = [user_agent_rotator.get_random_user_agent() for _ in range(100)]

chrome_x_client_data_map = {
    "114": "CIy2yQEIpbbJAQjBtskBCKmdygEIqKPKAQ==",
    "115": "CJn2yQEIorbJAQjBtskBCKmdygEIqZPKAQ==",
    "116": "CKe2yQEImtbJAQjBtskBCKmdygEIrqPKAQ==",
    "117": "CIy3yQEIotbJAQjBtskBCKmdygEIs6PKAQ==",
    "118": "CJq2yQEIpbbJAQjBtskBCKmdygEItKPKAQ==",
    "119": "CKr3yQEIptcJAQjBtskBCKmdygEIuKPKAQ==",
    "120": "CLa3yQEIqtgJAQjBtskBCKmdygEIvqPKAQ=="
}
