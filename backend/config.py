import os
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------------------------------


_host: str = "83.175.125.85"
# _host: str = "localhost"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"
_cache_host: str = os.getenv('CACHE_DB', "127.0.0.1")

# ----------------------------------------------------------------------------------------------------------------------


class Config:
    db_url: str = f'mysql://{_user}:{_password}@{_host}/{_dbname}'
    db_cache_url: str = f'mysql://{_user}:{_password}@{_cache_host}/bbf_inf_cache'
    debug: bool = True
    update_cache: str = "expired"  # always, never, expired
    secret: bytes = b'mdmekrifglvkcmalqwoeircbnfkhgpolc'
    cache_dir: str = os.getenv('CACHE_DIR', str(Path.home() / ".cache/dashboard"))

# ----------------------------------------------------------------------------------------------------------------------
