"""
API hooks for network stuff.
"""

from .api import net
from .error import handle_nonzero_success

__all__ = ['AddConnection']


def AddConnection(
    remote_name,
    type=net.RESOURCETYPE_ANY,
    local_name=None,
    provider_name=None,
    user=None,
    password=None,
    flags=0,
):
    resource = net.NETRESOURCE(
        type=type,
        remote_name=remote_name,
        local_name=local_name,
        provider_name=provider_name,
        # WNetAddConnection2 ignores the other members of NETRESOURCE
    )

    handle_nonzero_success(net.WNetAddConnection2(resource, password, user, flags))
