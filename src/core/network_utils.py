from functools import wraps
from urllib.error import HTTPError, URLError

def handle_download_errors(func):
    """
    Wrapper to handle download errors

    :param func: The function to wrap
    :return: The result of the function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        label = kwargs.get("label", func.__name__)
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            print(f"HTTP Error for {label}: {e.code} - {e.reason}")
        except URLError as e:
            print(f"URL Error for {label}: {e.reason}")
        except OSError as e:
            print(f"OS Error for {label}: {e.strerror}")
        except Exception as e:
            print(f"Unexpected error for {label}: {e}")
        return None
    return wrapper