# __init__.py (Client-Side - Final Version)
import rpyc
from datetime import datetime
from . import constants

class MetaTrader5:
    """
    The main client class for the Iris-MT5-Bridge.
    Uses RPyC for direct, robust remote procedure calls to the MT5 server in Wine.
    """
    
    # Make all constants available (e.g., mt5.TIMEFRAME_H1)
    for const in dir(constants):
        if const.isupper():
            locals()[const] = getattr(constants, const)

    def __init__(self, host='localhost', port=18812, timeout=300):
        """
        Connects to the RPyC server running in the Wine environment.
        """
        print("Connecting to Iris-MT5-Bridge server...")
        # Establish the connection
        self.__conn = rpyc.classic.connect(host, port)
        # Set a long timeout for potentially slow operations
        self.__conn._config['sync_request_timeout'] = timeout
        
        # self.bridge is the remote service object. We can call its exposed methods directly.
        self.bridge = self.__conn.root
        print("Bridge connected successfully.")

    def initialize(self, *args, **kwargs):
        """Initializes the MT5 terminal connection via the remote server."""
        print("Sending initialize command...")
        return self.bridge.exposed_initialize(*args, **kwargs)

    def shutdown(self):
        """Shuts down the MT5 terminal connection via the remote server."""
        print("Sending shutdown command...")
        return self.bridge.exposed_shutdown()

    def account_info(self):
        """Gets account information."""
        return self.bridge.exposed_account_info()

    def symbol_info(self, symbol: str):
        """Gets information about a specific symbol."""
        return self.bridge.exposed_symbol_info(symbol)

    def symbol_info_tick(self, symbol: str):
        """Gets the latest tick for a symbol."""
        return self.bridge.exposed_symbol_info_tick(symbol)
        
    def copy_rates_from_pos(self, symbol: str, timeframe, start_pos: int, count: int):
        """Gets historical rate data from a start position."""
        return self.bridge.exposed_copy_rates_from_pos(symbol, timeframe, start_pos, count)
    
    def copy_rates_from(self, symbol: str, timeframe, date_from: datetime, count: int):
        """
        Gets historical rate data from a start date.
        """
        # The datetime object is automatically handled by RPyC
        return self.bridge.exposed_copy_rates_from(symbol, timeframe, date_from, count)
    
    def order_send(self, request: dict):
        """Sends a trade request dictionary directly to the server."""
        return self.bridge.exposed_order_send(request)

    def positions_get(self, *args, **kwargs):
        """Gets all open positions."""
        return self.bridge.exposed_positions_get(*args, **kwargs)

    def order_check(self, request: dict):
        """Checks a trade request dictionary directly on the server."""
        return self.bridge.exposed_order_check(request)

    def last_error(self):
        """Gets the last error from the MT5 terminal."""
        return self.bridge.exposed_last_error()