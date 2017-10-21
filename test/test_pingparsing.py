# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import

from collections import namedtuple
import itertools

from pingparsing import EmptyPingStatisticsError
import pytest
import six

from .common import ping_parser
from .data import (
    PING_DEBIAN_SUCCESS,
)


PING_FEDORA_EMPTY_BODY = six.b("""
PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.

--- 192.168.0.1 ping statistics ---
""")
PING_WINDOWS_INVALID = """
Pinging 192.168.207.100 with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for 192.168.207.100:
"""

PingTestData = namedtuple("PingTestData", "value expected")

DEBIAN_SUCCESS = PingTestData(
    PING_DEBIAN_SUCCESS,
    {
        "packet_transmit": 60,
        "packet_receive": 60,
        "packet_loss_rate": 0.0,
        "packet_loss_count": 0,
        "rtt_min": 61.425,
        "rtt_avg": 99.731,
        "rtt_max": 212.597,
        "rtt_mdev": 27.566,
        "packet_duplicate_rate": 0,
        "packet_duplicate_count": 0,
    })
DEBIAN_UNREACHABLE_0 = PingTestData(
    """PING 192.168.207.100 (192.168.207.100) 56(84) bytes of data.

--- 192.168.207.100 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 4009ms
""",
    {
        "packet_transmit": 5,
        "packet_receive": 0,
        "packet_loss_rate": 100.0,
        "packet_loss_count": 5,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": 0,
    })
DEBIAN_UNREACHABLE_1 = PingTestData(
    DEBIAN_UNREACHABLE_0.value + "\n", DEBIAN_UNREACHABLE_0.expected)
DEBIAN_UNREACHABLE_2 = PingTestData(
    DEBIAN_UNREACHABLE_1.value + "\n", DEBIAN_UNREACHABLE_0.expected)

FEDORA_DUP_LOSS = PingTestData(
    """PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.

--- 192.168.0.1 ping statistics ---
1688 packets transmitted, 1553 received, +1 duplicates, 7% packet loss, time 2987ms
rtt min/avg/max/mdev = 0.282/0.642/11.699/0.699 ms, pipe 2, ipg/ewma 1.770/0.782 ms
""",
    {
        "packet_receive": 1553,
        "packet_transmit": 1688,
        "packet_loss_rate": 7.997630331753558,
        "packet_loss_count": 135,
        "rtt_min": 0.282,
        "rtt_max": 11.699,
        "rtt_mdev": 0.699,
        "rtt_avg": 0.642,
        "packet_duplicate_rate": 0.0643915003219575,
        "packet_duplicate_count": 1,
    })
FEDORA_UNREACHABLE = PingTestData(
    """PING 192.168.207.100 (192.168.207.100) 56(84) bytes of data.
From 192.168.207.128 icmp_seq=1 Destination Host Unreachable
From 192.168.207.128 icmp_seq=2 Destination Host Unreachable
From 192.168.207.128 icmp_seq=3 Destination Host Unreachable
From 192.168.207.128 icmp_seq=4 Destination Host Unreachable
From 192.168.207.128 icmp_seq=5 Destination Host Unreachable

--- 192.168.207.100 ping statistics ---
5 packets transmitted, 0 received, +5 errors, 100% packet loss, time 4003ms
""",
    {
        "packet_transmit": 5,
        "packet_receive": 0,
        "packet_loss_rate": 100.0,
        "packet_loss_count": 5,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": 0,
    })

OSX_SUCCESS_0 = PingTestData(
    """PING google.com (172.217.6.238): 56 data bytes
64 bytes from 172.217.6.238: icmp_seq=0 ttl=53 time=20.482 ms
64 bytes from 172.217.6.238: icmp_seq=1 ttl=53 time=32.550 ms
64 bytes from 172.217.6.238: icmp_seq=2 ttl=53 time=32.013 ms
64 bytes from 172.217.6.238: icmp_seq=3 ttl=53 time=28.498 ms
64 bytes from 172.217.6.238: icmp_seq=4 ttl=53 time=46.093 ms

--- google.com ping statistics ---
5 packets transmitted, 5 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 20.482/31.927/46.093/8.292 ms
""",
    {
        "packet_duplicate_count": None,
        "packet_duplicate_rate": None,
        "packet_loss_count": 0,
        "packet_loss_rate": 0.0,
        "packet_receive": 5,
        "packet_transmit": 5,
        "rtt_avg": 31.927,
        "rtt_max": 46.093,
        "rtt_mdev": 8.292,
        "rtt_min": 20.482,
    })
OSX_SUCCESS_1 = PingTestData(
    """PING github.com (192.30.255.113): 56 data bytes

--- github.com ping statistics ---
10 packets transmitted, 10 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 218.391/283.477/405.879/70.170 ms
""",
    {
        "packet_duplicate_count": None,
        "packet_duplicate_rate": None,
        "packet_loss_count": 0,
        "packet_loss_rate": 0.0,
        "packet_receive": 10,
        "packet_transmit": 10,
        "rtt_avg": 283.477,
        "rtt_max": 405.879,
        "rtt_mdev": 70.170,
        "rtt_min": 218.391,
    })
OSX_UNREACHABLE_0 = PingTestData(
    """PING twitter.com (59.24.3.173): 56 data bytes
^C
--- twitter.com ping statistics ---
59 packets transmitted, 0 packets received, 100.0% packet los
""",
    {
        "packet_transmit": 59,
        "packet_receive": 0,
        "packet_loss_rate": 100.0,
        "packet_loss_count": 59,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": None,
    })
OSX_UNREACHABLE_1 = PingTestData(
    """PING twitter.com (31.13.78.66): 56 data bytes

--- twitter.com ping statistics ---
10 packets transmitted, 0 packets received, 100.0% packet loss
""",
    {
        "packet_transmit": 10,
        "packet_receive": 0,
        "packet_loss_rate": 100.0,
        "packet_loss_count": 10,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": None,
    })

ALPINE_LINUX_SUCCESS = PingTestData(
    """PING heise.de (193.99.144.80): 56 data bytes

--- heise.de ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 0.638/0.683/0.746 ms
""",
    {
        "packet_duplicate_count": 0,
        "packet_duplicate_rate": 0,
        "packet_loss_count": 0,
        "packet_loss_rate": 0.0,
        "packet_receive": 5,
        "packet_transmit": 5,
        "rtt_avg": 0.683,
        "rtt_max": 0.746,
        "rtt_mdev": None,
        "rtt_min": 0.638,
    })
ALPINE_LINUX_DUP_LOSS = PingTestData(
    """PING 192.168.2.106 (192.168.2.106): 56 data bytes
64 bytes from 192.168.2.106: seq=0 ttl=64 time=0.936 ms
64 bytes from 192.168.2.106: seq=0 ttl=64 time=1.003 ms (DUP!)
64 bytes from 192.168.2.106: seq=1 ttl=64 time=0.802 ms
64 bytes from 192.168.2.106: seq=2 ttl=64 time=0.696 ms
64 bytes from 192.168.2.106: seq=3 ttl=64 time=0.664 ms
64 bytes from 192.168.2.106: seq=4 ttl=64 time=1.194 ms
64 bytes from 192.168.2.106: seq=5 ttl=64 time=0.613 ms
64 bytes from 192.168.2.106: seq=6 ttl=64 time=0.898 ms
64 bytes from 192.168.2.106: seq=8 ttl=64 time=1.066 ms
64 bytes from 192.168.2.106: seq=9 ttl=64 time=1.144 ms
64 bytes from 192.168.2.106: seq=9 ttl=64 time=1.219 ms (DUP!)

--- 192.168.2.106 ping statistics ---
10 packets transmitted, 9 packets received, 2 duplicates, 10% packet loss
round-trip min/avg/max = 0.613/0.930/1.219 ms
""",
    {
        "packet_duplicate_count": 2,
        "packet_duplicate_rate": 22.22222222222222,
        "packet_loss_count": 1,
        "packet_loss_rate": 9.999999999999998,
        "packet_receive": 9,
        "packet_transmit": 10,
        "rtt_min": 0.613,
        "rtt_avg": 0.93,
        "rtt_max": 1.219,
        "rtt_mdev": None,
    })

WINDOWS_SUCCESS = PingTestData(
    # ping google.com -n 10:
    #   Windows 7 SP1
    """Pinging google.com [216.58.196.238] with 32 bytes of data:
Reply from 216.58.196.238: bytes=32 time=87ms TTL=51
Reply from 216.58.196.238: bytes=32 time=97ms TTL=51
Reply from 216.58.196.238: bytes=32 time=56ms TTL=51
Reply from 216.58.196.238: bytes=32 time=95ms TTL=51
Reply from 216.58.196.238: bytes=32 time=194ms TTL=51
Reply from 216.58.196.238: bytes=32 time=98ms TTL=51
Reply from 216.58.196.238: bytes=32 time=93ms TTL=51
Reply from 216.58.196.238: bytes=32 time=96ms TTL=51
Reply from 216.58.196.238: bytes=32 time=96ms TTL=51
Reply from 216.58.196.238: bytes=32 time=165ms TTL=51

Ping statistics for 216.58.196.238:
    Packets: Sent = 10, Received = 10, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 56ms, Maximum = 194ms, Average = 107ms
""",
    {
        "packet_transmit": 10,
        "packet_receive": 10,
        "packet_loss_rate": 0.0,
        "packet_loss_count": 0,
        "rtt_min": 56,
        "rtt_avg": 107,
        "rtt_max": 194,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": None,
    })
WINDOWS_UNREACHABLE_0 = PingTestData(
    """Pinging 192.168.207.100 with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for 192.168.207.100:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
""",
    {
        "packet_transmit": 4,
        "packet_receive": 0,
        "packet_loss_rate": 100.0,
        "packet_loss_count": 4,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "rtt_mdev": None,
        "packet_duplicate_rate": None,
        "packet_duplicate_count": None,
    })
WINDOWS_UNREACHABLE_1 = PingTestData(
    WINDOWS_UNREACHABLE_0.value + "\n", WINDOWS_UNREACHABLE_0.expected)
WINDOWS_UNREACHABLE_2 = PingTestData(
    WINDOWS_UNREACHABLE_1.value + "\n", WINDOWS_UNREACHABLE_0.expected)


class Test_PingParsing_parse(object):

    @pytest.mark.parametrize(["test_data"], [
        [DEBIAN_SUCCESS],
        [DEBIAN_UNREACHABLE_0],
        [DEBIAN_UNREACHABLE_1],
        [DEBIAN_UNREACHABLE_2],
        [FEDORA_DUP_LOSS],
        [FEDORA_UNREACHABLE],
        [OSX_SUCCESS_0],
        [OSX_SUCCESS_1],
        [OSX_UNREACHABLE_0],
        [OSX_UNREACHABLE_1],
        [ALPINE_LINUX_SUCCESS],
        [ALPINE_LINUX_DUP_LOSS],
        [WINDOWS_SUCCESS],
        [WINDOWS_UNREACHABLE_0],
        [WINDOWS_UNREACHABLE_1],
        [WINDOWS_UNREACHABLE_2],
    ])
    def test_normal_text(self, ping_parser, test_data):
        ping_parser.parse(test_data.value)

        print("[input text]\n{}".format(test_data.value))

        assert ping_parser.as_dict() == test_data.expected

    def test_empty(self, ping_parser):
        ping_parser.parse("""
PING google.com (216.58.196.238) 56(84) bytes of data.

--- google.com ping statistics ---
60 packets transmitted, 60 received, 0% packet loss, time 59153ms
rtt min/avg/max/mdev = 61.425/99.731/212.597/27.566 ms
""")
        ping_parser.parse("")

        assert ping_parser.packet_transmit is None
        assert ping_parser.packet_receive is None
        assert ping_parser.packet_loss_rate is None
        assert ping_parser.rtt_min is None
        assert ping_parser.rtt_avg is None
        assert ping_parser.rtt_max is None
        assert ping_parser.rtt_mdev is None
        assert ping_parser.packet_duplicate_count is None

    @pytest.mark.parametrize(["value", "expected"], [
        [PING_FEDORA_EMPTY_BODY, EmptyPingStatisticsError],
        [PING_WINDOWS_INVALID, EmptyPingStatisticsError],
    ])
    def test_exception(self, ping_parser, value, expected):
        with pytest.raises(expected):
            ping_parser.parse(value)
