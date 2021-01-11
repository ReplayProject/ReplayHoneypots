import pytest
import trio
from Listener import Listener


TEST_PORT = 1337
WAIT_TIME = 0.1

class TestService:
    def __init__(self, name, port, protocol, response_model):
        self.name = name
        self.port = port
        self.protocol = protocol
        self.response_model = response_model

tcp_service = TestService("test", TEST_PORT, "TCP",
[
    {
        "request": {
            "payload": "4869"
        },
        "responses": [
            {
                "payload": "48656c6c6f"
            }
        ]
    },
    {
        "request": {
            "payload": "486f772061726520796f753f"
        },
        "responses": [
            {
                "payload": "476f6f64"
            }
        ]
    }
])

tcp_service2 = TestService("test", TEST_PORT, "TCP",
[
    {
        "request": None,
        "responses": [
            {
                "payload": "48656c6c6f"
            }
        ]
    },
    {
        "request": {
            "payload": "486f772061726520796f753f"
        },
        "responses": [
            {
                "payload": "476f6f64"
            }
        ]
    }
])

udp_service = TestService("test", TEST_PORT, "UDP",
[
    {
        "request": {
            "payload": "4869"
        },
        "responses": [
            {
                "payload": "48656c6c6f"
            }
        ]
    },
        {
        "request": {
            "payload": "486f772061726520796f753f"
        },
        "responses": [
            {
                "payload": "476f6f64"
            }
        ]
    }
])

def e(s):
    """
    Helper function to turn a string into hex
    """
    return "".join(hex(ord(x))[2:] for x in s)


@pytest.fixture
def listen():
    """
    Fixture to boilerplate a function to get  port listeners running
    """

    def _(*args, **kwargs):
        from Listener import Listener

        return Listener(TEST_PORT, args[0], args[1], args[2], args[3])

    return _


class TestUDPListener:
    """
    Check behaivor of listeners and replay functionality
    """

    async def testListenerInit(self, listen, nursery):
        listener = listen(udp_service, "UDP", 0, nursery)
        assert len(nursery.child_tasks) == 0
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)
        assert len(nursery.child_tasks) == 1, "Task should make it into the nursery"

    async def testListenerReplay(self, listen, nursery):
        listener = listen(udp_service, "UDP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:
            await sock.sendto("Hi".encode("utf8"), ("", TEST_PORT))
            data = ""
            with trio.move_on_after(3):
                data, addr = await sock.recvfrom(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == "Hello", "response should be premade payload"
            assert nursery._closed is False

    async def testListenerPayload(self, listen, nursery):
        listener1 = listen(udp_service, "UDP", 0, nursery)
        nursery.start_soon(listener1.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:
            await sock.sendto("How are you?".encode("utf8"), ("", TEST_PORT))
            data = ""
            with trio.move_on_after(3):
                data, addr = await sock.recvfrom(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == "Good", "response should be premade payload"
            await trio.sleep(WAIT_TIME)
            assert nursery._closed is False

    async def testMultipleClients(self, listen, nursery):
        listener = listen(udp_service, "UDP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        for x in range(1, 150):
            with trio.socket.socket(
                trio.socket.AF_INET, trio.socket.SOCK_DGRAM
            ) as sock:
                await sock.sendto("Hi".encode("utf8"), ("", TEST_PORT))
                data = ""
                with trio.move_on_after(3):
                    data, addr = await sock.recvfrom(1024)
                # print("got: ", data)
                # print("from: ", addr)
                assert (
                    data.decode("utf8") == "Hello"
                ), "response should be premade payload"

    async def testNonMatchingRequest(self, listen, nursery):
        listener1 = listen(udp_service, "UDP", 0, nursery)
        nursery.start_soon(listener1.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:
            await sock.sendto("asdpofijadsf".encode("utf8"), ("", TEST_PORT))
            with trio.move_on_after(3):
                data = await sock.recv(1024)
                assert (False), "should not have responded"

class TestTCPListener:
    """
    Check behaivor of listeners and replay functionality
    """

    async def testListenerInit(self, listen, nursery):
        listener = listen(tcp_service, "TCP", 0, nursery)
        assert len(nursery.child_tasks) == 0
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)
        assert len(nursery.child_tasks) == 1, "Task should make it into the nursery"

    async def testListenerReplay(self, listen, nursery):
        listener = listen(tcp_service, "TCP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_STREAM) as sock:
            await sock.connect(("", TEST_PORT))
            await sock.send("Hi".encode("utf8"))
            data = await sock.recv(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == "Hello", "response should be premade payload"
            assert nursery._closed is False

    async def testListenerPayload(self, listen, nursery):
        listener1 = listen(tcp_service, "TCP", 0, nursery)
        nursery.start_soon(listener1.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_STREAM) as sock:
            await sock.connect(("", TEST_PORT))
            await sock.send("How are you?".encode("utf8"))
            data = await sock.recv(1024)
            # print("got: ", data)
            # print("from: ", addr)
            assert data.decode("utf8") == "Good", "response should be premade payload"
            await trio.sleep(WAIT_TIME)
            assert nursery._closed is False

    async def testMultipleClients(self, listen, nursery):
        listener = listen(tcp_service, "TCP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        for _ in range(1, 150):
            with trio.socket.socket(
                trio.socket.AF_INET, trio.socket.SOCK_STREAM
            ) as sock:
                await sock.connect(("", TEST_PORT))
                await sock.send("Hi".encode("utf8"))
                data = await sock.recv(1024)
                # print("got: ", data)
                # print("from: ", addr)
                assert (
                    data.decode("utf8") == "Hello"
                ), "response should be premade payload"

    async def testNonMatchingRequest(self, listen, nursery):
        listener = listen(tcp_service, "TCP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(
            trio.socket.AF_INET, trio.socket.SOCK_STREAM
        ) as sock:
            await sock.connect(("", TEST_PORT))
            await sock.send("adspofijadsf".encode("utf8"))
            with trio.move_on_after(3):
                data = await sock.recv(1024)
                assert (False), "should not have responded"
            

    # Test that socket can send an initial message before a client sends anything
    async def testInitialResponse(self, listen, nursery):
        listener = listen(tcp_service2, "TCP", 0, nursery)
        nursery.start_soon(listener.handler)
        await trio.sleep(WAIT_TIME)

        with trio.socket.socket(
            trio.socket.AF_INET, trio.socket.SOCK_STREAM
        ) as sock:
            await sock.connect(("", TEST_PORT))
            data = None
            with trio.move_on_after(3):
                data = await sock.recv(1024)            
            assert data is not None and data.decode("utf8") == "Hello"
