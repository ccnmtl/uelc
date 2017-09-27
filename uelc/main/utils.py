import random
import string
from django.core.cache import cache


def clear_handler_cache(node):
    cache.delete('uelc.{}.get_part_by_section'.format(node.pk))
    cache.delete('uelc.{}.is_next_curveball'.format(node.pk))


def random_string(n):
    """Generate a random string of length n."""
    return ''.join(
        random.choice(  # nosec
            string.ascii_uppercase + string.digits) for _ in range(n))
