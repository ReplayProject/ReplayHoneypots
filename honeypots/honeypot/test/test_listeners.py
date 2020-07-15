import pytest
import trio
from TCPPortListener import TCPPortListener


TEST_PORT = 1337
WAIT_TIME = 0.1


def e(s):
    """
    Helper function to turn a string into hex
    """
    return "".join(hex(ord(x))[2:] for x in s)


@pytest.fixture
def udp():
    """
    Fixture to boilerplate a function to get UDP port listeners running
    """

    def _(*args, **kwargs):
        from UDPPortListener import UDPPortListener

        return UDPPortListener(TEST_PORT, args[0], args[1], args[2])

    return _


class TestUDPListener:
    """
    Check behaivor of listeners and replay functionality
    """

    async def testListenerInit(self, udp, nursery):
        string = "hello world"
        listener = udp(e(string), 0, nursery)
        assert len(nursery.child_tasks) == 0
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)
        assert len(nursery.child_tasks) == 1, "Task should make it into the nursery"

    async def testListenerReplay(self, udp, nursery):
        string = "hello world"
        listener = udp(e(string), 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:
            await sock.sendto("hi".encode("utf8"), ("", TEST_PORT))
            data, addr = await sock.recvfrom(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == string, "response should be premade payload"
            assert nursery._closed is False

    async def testListenerPayload(self, udp, nursery):
        string = "[][]6[]8[]7657%$^#%^%$#^%"
        listener1 = udp(e(string), 0, nursery)
        nursery.start_soon(listener1.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:
            await sock.sendto("hi".encode("utf8"), ("", TEST_PORT))
            data, addr = await sock.recvfrom(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == string, "response should be premade payload"
            await trio.sleep(WAIT_TIME)
            assert nursery._closed is False

    async def testMultipleClients(self, udp, nursery):
        string = "normal text"
        listener = udp(e(string), 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        for x in range(1, 150):
            with trio.socket.socket(
                trio.socket.AF_INET, trio.socket.SOCK_DGRAM
            ) as sock:
                await sock.sendto(("hi" + str(x)).encode("utf8"), ("", TEST_PORT))
                data, addr = await sock.recvfrom(1024)
                # print("got: ", data)
                # print("from: ", addr)
                assert (
                    data.decode("utf8") == string
                ), "response should be premade payload"


@pytest.fixture
def tcp():
    """
    Fixture to boilerplate a function ot get UDP port listeners
    """

    def _(*args, **kwargs):
        return TCPPortListener(TEST_PORT, args[0], args[1], args[2])

    return _


class TestTCPListener:
    """
    Check behaivor of listeners and replay functionality
    """

    async def testListenerInit(self, tcp, nursery):
        string = "hello world"
        listener = tcp(e(string), 0, nursery)
        assert len(nursery.child_tasks) == 0
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)
        assert len(nursery.child_tasks) == 1, "Task should make it into the nursery"

    async def testListenerReplay(self, tcp, nursery):
        string = "hello world"
        listener = tcp(e(string), 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_STREAM) as sock:
            await sock.connect(("", TEST_PORT))
            await sock.send("hi".encode("utf8"))
            data = await sock.recv(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == string, "response should be premade payload"
            assert nursery._closed is False

    async def testListenerPayload(self, tcp, nursery):
        string = "[][]6[]8[]7657%$^#%^%$#^%"
        listener1 = tcp(e(string), 0, nursery)
        nursery.start_soon(listener1.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_STREAM) as sock:
            await sock.connect(("", TEST_PORT))
            await sock.send("hi".encode("utf8"))
            data = await sock.recv(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == string, "response should be premade payload"
            await trio.sleep(WAIT_TIME)
            assert nursery._closed is False

    async def testMultipleClients(self, tcp, nursery):
        string = "normal text"
        listener = tcp(e(string), 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        for _ in range(1, 150):
            with trio.socket.socket(
                trio.socket.AF_INET, trio.socket.SOCK_STREAM
            ) as sock:
                await sock.connect(("", TEST_PORT))
                await sock.send("hi".encode("utf8"))
                data = await sock.recv(1024)
                # print("got: ", data)
                # print("from: ", addr)
                assert (
                    data.decode("utf8") == string
                ), "response should be premade payload"


# Sample Fake tests
async def test_sleep():
    start_time = trio.current_time()
    await trio.sleep(1)
    end_time = trio.current_time()
    assert end_time - start_time >= 1


async def test_sleep_efficiently_and_reliably(autojump_clock):
    start_time = trio.current_time()
    await trio.sleep(1)
    end_time = trio.current_time()
    assert abs(start_time - end_time) == 1
