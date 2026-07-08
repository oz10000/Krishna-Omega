
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
import config

def is_time_valid() -> bool:
    now = datetime.now(timezone.utc)
    return now.hour in config.VALID_HOURS
