from django.core.cache import cache


def clear_handler_cache(node):
    cache.delete('uelc.{}.get_part_by_section'.format(node.pk))
    cache.delete('uelc.{}.is_next_curveball'.format(node.pk))
    cache.delete('uelc.{}.get_tree_depth'.format(node.pk))
