from TCPPortListener import TCPPortListener
from ConfigTunnel import ConfigTunnel

import trio
import pytest

TEST_PORT = 1337
WAIT_TIME = 0.1

from trio.testing import open_stream_to_socket_listener


class TestConfigTunnel:
    async def test_advanced_handler(self, nursery):
        """
        Setup both ends of the tunnel with a connection to localhost
        """
        stunnel = ConfigTunnel("server")
        ctunnel = ConfigTunnel("client", "localhost")

        # Helper Variables & Functions
        echoflag = False
        echoPayload = []

        def handle_server_echo(x):
            nonlocal echoflag, echoPayload
            echoflag = True
            echoPayload = x
            return "echo value"

        doneflag = False
        donePayload = []

        def handle_client_done(x):
            nonlocal doneflag, donePayload
            doneflag = True
            donePayload = x

        # Server Handler Setup
        stunnel.setHandler("test", handle_server_echo)
        nursery.start_soon(stunnel.listen)
        await trio.sleep(WAIT_TIME)

        ctunnel.setHandler("done", handle_client_done)
        nursery.start_soon(ctunnel.connect)
        await trio.sleep(WAIT_TIME)

        # Wait and send a "command"
        await ctunnel.send("test with a somewhat longer message")
        await trio.sleep(WAIT_TIME)

        assert echoflag
        assert echoPayload == ["with", "a", "somewhat", "longer", "message"]

        # Client received response and payload
        assert doneflag
        assert donePayload == ["echo", "value"]

    async def test_basic_handler(self, nursery):
        """
        Setup both ends of the tunnel with a connection to localhost
        """
        stunnel = ConfigTunnel("server")
        ctunnel = ConfigTunnel("client", "localhost")

        flag = False

        def handle_test(x):
            nonlocal flag
            print("handle: ", x)
            flag = True

        # Server Handler Setup
        stunnel.setHandler("test", handle_test)
        nursery.start_soon(stunnel.listen)
        await trio.sleep(WAIT_TIME)

        nursery.start_soon(ctunnel.connect)
        await trio.sleep(WAIT_TIME)

        await ctunnel.send("test with a longer command")
        await trio.sleep(WAIT_TIME)

        assert flag


# DEPRECATED CONFIG TUNNEL TESTS KEPT AS REFERENCE


# class TestConfigTunnel(unittest.TestCase):
#     """
#     Handles testing for the ConfigTunnel module
#     """
#     def setUp(self):
#         """
#         Setup both ends of the tunnel with a connection to localhost
#         """
#         self.stunnel = ConfigTunnel('server')
#         self.ctunnel = ConfigTunnel('client', "localhost")

#     def tearDown(self):
#         """
#         Get ready for the next test
#         """
#         self.ctunnel.stop()
#         self.stunnel.stop()
#         time.sleep(2)
#         self.ctunnel.join()
#         self.stunnel.join()

#     def test_fulltest(self):
#         # Server & Client Start
#         self.stunnel.start()
#         self.ctunnel.start()
#         time.sleep(1)
#         self.assertTrue(True)

#     def test_init(self):
#         """
#         Test that server/client start and connect to eachother
#         """
#         # Server & Client Start
#         self.stunnel.start()
#         self.ctunnel.start()
#         time.sleep(1)

#         self.assertTrue(self.stunnel.ready)
#         self.assertTrue(self.ctunnel.ready)

#     def test_basic_handlers(self):
#         """
#         Test that we can use the tunnel with a one way handler
#         """
#         # Helper Variables & Functions
#         handle_test = MagicMock(return_value=None)
#         # Server Handler Setup
#         self.stunnel.setHandler("test", handle_test)
#         # Server & Client Start
#         self.stunnel.start()
#         self.ctunnel.start()
#         # Wait and send a "command"
#         time.sleep(2)
#         self.ctunnel.send("test")
#         # Final checks
#         time.sleep(1)
#         self.assertTrue(handle_test.called)

#     def test_advanced_handlers(self):
#         """
#         More complex usage of handlers and passing simple data
#         """
#         # Helper Variables & Functions
#         handle_server_echo = MagicMock(return_value="echo value")
#         handle_client_done = MagicMock(return_value=None)
#         # Server & Client Setup
#         self.stunnel.setHandler("test", handle_server_echo)
#         self.stunnel.start()
#         self.ctunnel.setHandler("done", handle_client_done)
#         self.ctunnel.start()
#         # Wait and send a "command"
#         time.sleep(2)
#         self.ctunnel.send("test with a somewhat longer message")
#         # Final checks
#         time.sleep(1)
#         # Server received command
#         self.assertTrue(handle_server_echo.called)
#         server_expected = ['with', 'a', 'somewhat', 'longer', 'message']
#         handle_server_echo.assert_called_once_with(server_expected)
#         # Client received response and payload
#         self.assertTrue(handle_client_done.called)
#         handle_client_done.assert_called_once_with(["echo", "value"])
