# ----------------------------------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------------------------------


_host: str = "83.175.125.85"
# _host: str = "localhost"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"

# ----------------------------------------------------------------------------------------------------------------------


class Config:
    db_url: str = f'mysql://{_user}:{_password}@{_host}/{_dbname}'
    db_cache_url: str = f'mysql://{_user}:{_password}@localhost/bbf_inf_cache'
    debug: bool = True
    update_cache: str = "expired"  # always, never, expired
    secret: bytes = b'mdmekrifglvkcmalqwoeircbnfkhgpolc'

# ----------------------------------------------------------------------------------------------------------------------
