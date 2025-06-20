# server.py (Refactored Final Version)
"""
Iris-MT5-Bridge Server

This script runs an RPyC (Remote Python Call) server that the main client
connects to. It runs within the Wine environment and directly interacts with
the official MetaTrader 5 Python library. This version exposes a full suite of
functions to be called directly by the client.
"""
import rpyc
import threading
import time
from datetime import datetime
from plumbum import cli
from rpyc.utils.server import ThreadedServer
from rpyc.core import SlaveService
import MetaTrader5 as mt5 # type: ignore
import emoji

# --- Centralized Helper Functions ---

def _get_mt5_instance():
    """Ensures MT5 is initialized and returns the module."""
    # This helper prevents re-initializing on every call.
    if not mt5.terminal_info():
        if not mt5.initialize():
            print(f"Server Error: initialize() failed, error code = {mt5.last_error()}")
            return None
    return mt5

def _serialize_rates(rates_array):
    """Helper to convert NumPy rate arrays into a list of dicts for safe transport."""
    if rates_array is None:
        return None
    try:
        # This is a fast and reliable way to convert the structured array
        return [dict(zip(rec.dtype.names, rec)) for rec in rates_array]
    except Exception as e:
        return {"error": f"Failed to serialize rates array: {e}"}
        
# --- Definitions for All Remotely Callable Functions ---

def exposed_initialize(self, *args, **kwargs):
    m = _get_mt5_instance()
    if m: return m.initialize(*args, **kwargs)

def exposed_shutdown(self):
    m = _get_mt5_instance()
    if m: return m.shutdown()

def exposed_account_info(self):
    m = _get_mt5_instance()
    if m: return m.account_info()

def exposed_symbol_info(self,symbol):
    m = _get_mt5_instance()
    if m: return m.symbol_info(symbol)

def exposed_symbol_info_tick(self,symbol):
    m = _get_mt5_instance()
    if m: return m.symbol_info_tick(symbol)

def exposed_copy_rates_from_pos(self,symbol, timeframe, start_pos, count):
    m = _get_mt5_instance()
    if not m: return None
    rates_array = m.copy_rates_from_pos(symbol, timeframe, start_pos, count)
    return _serialize_rates(rates_array)

def exposed_copy_rates_from(self, symbol, timeframe, date_from, count):
    m = _get_mt5_instance()
    if not m: return None

    # The client sends a datetime object, RPyC transfers it.
    # To be safe and avoid timezone issues, we will convert it to a
    # simple integer timestamp, which the real MT5 library accepts.
    utc_from_timestamp = int(date_from.timestamp())

    print(f"Server: executing copy_rates_from for {symbol} with timestamp {utc_from_timestamp}...")
    
    rates_array = m.copy_rates_from(symbol, timeframe, utc_from_timestamp, count)
    
    # Add a check here for what the function returned
    if rates_array is None:
        print(f"   --> The real mt5.copy_rates_from returned None. Error: {m.last_error()}")

    return _serialize_rates(rates_array)


def exposed_order_send(self,request):
    m = _get_mt5_instance()
    if m: return m.order_send(request)

def exposed_positions_get(self, *args, **kwargs):
    m = _get_mt5_instance()
    if m: return m.positions_get(*args, **kwargs)
    
def exposed_order_check(self, request):
    m = _get_mt5_instance()
    if m: return m.order_check(self, request)

def exposed_last_error(self):
    m = _get_mt5_instance()
    if m: return m.last_error()

def heartbeat_thread(interval_seconds=120):
    """A simple thread that prints a life signal every X seconds."""
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(emoji.emojize(f":sparkle: [{timestamp}] Server is alive and operating normally."))
        time.sleep(interval_seconds)


class ClassicServer(cli.Application):
    """The main server application class, handles command-line arguments."""
    port = cli.SwitchAttr(["-p", "--port"], cli.Range(0, 65535), default=18812,
                          help="The TCP listener port")
    host = cli.SwitchAttr(["--host"], str, default="localhost", help="The host to bind to.")
    
    def main(self):
        """The main entry point of the server application."""

        t = ThreadedServer(SlaveService, hostname=self.host, port=self.port,
                           reuse_addr=True)
        
        # --- Dynamically attach all our 'exposed' functions to the RPyC service ---
        #print("Attaching remote functions to the server...")
        t.service.exposed_initialize = exposed_initialize
        t.service.exposed_shutdown = exposed_shutdown
        t.service.exposed_account_info = exposed_account_info
        t.service.exposed_symbol_info = exposed_symbol_info
        t.service.exposed_symbol_info_tick = exposed_symbol_info_tick
        t.service.exposed_copy_rates_from_pos = exposed_copy_rates_from_pos
        t.service.exposed_copy_rates_from = exposed_copy_rates_from # Our new function
        t.service.exposed_order_send = exposed_order_send
        t.service.exposed_positions_get = exposed_positions_get
        t.service.exposed_order_check = exposed_order_check
        t.service.exposed_last_error = exposed_last_error
        #print("All functions attached.")
        
        print(emoji.emojize(f":laptop: Iris-MT5-Bridge server started on {self.host}:{self.port} :laptop:", language='alias'))
        t.start()

heartbeat = threading.Thread(target=heartbeat_thread, daemon=True)
heartbeat.start()

if __name__ == "__main__":
    ClassicServer.run()