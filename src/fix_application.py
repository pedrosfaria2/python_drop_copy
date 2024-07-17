import quickfix as fix
import os
import logging
from datetime import datetime

class FIXApplication(fix.Application):
    def __init__(self, raw_data: str):
        super().__init__()
        self.raw_data = raw_data
        self.logger = logging.getLogger('FIXApplication')
        self._setup_logger()

    import quickfix as fix
import os
import logging
from datetime import datetime

class FIXApplication(fix.Application):
    def __init__(self, raw_data: str):
        super().__init__()
        self.raw_data = raw_data
        self.logger = logging.getLogger('FIXApplication')
        self._setup_logger()

    def _setup_logger(self) -> None:
        """
        Sets up the logger for the FIX application.
        """
        try:
            log_date = datetime.now().strftime("%Y-%m-%d")
            session_log_filename = f"human_readable_logs/{log_date}_fix.log"
            communal_log_filename = "human_readable_logs/communal_fix.log"
            os.makedirs(os.path.dirname(session_log_filename), exist_ok=True)

            session_handler = logging.FileHandler(session_log_filename)
            communal_handler = logging.FileHandler(communal_log_filename, mode='a')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            session_handler.setFormatter(formatter)
            communal_handler.setFormatter(formatter)

            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(session_handler)
            self.logger.addHandler(communal_handler)

            # Ensure no logs are sent to the console
            self.logger.propagate = False

            # Setup message logs
            message_log_filename = f"human_readable_logs/{log_date}_messages.current.log"
            communal_message_log_filename = "human_readable_logs/communal_messages.current.log"
            os.makedirs(os.path.dirname(message_log_filename), exist_ok=True)

            self.session_message_log = open(message_log_filename, 'a')
            self.communal_message_log = open(communal_message_log_filename, 'a')
        except Exception as e:
            self.logger.error(f"Error setting up logger: {e}")
            raise

    def format_fix_message(self, message: fix.Message) -> str:
        """
        Formats a FIX message into a more readable format.

        Args:
            message (fix.Message): The FIX message to format.

        Returns:
            str: The formatted message.
        """
        fields = message.toString().split('\x01')
        formatted_message = ' | '.join(f'{field}' for field in fields if field)
        return formatted_message

    def onCreate(self, sessionID: fix.SessionID) -> None:
        """
        Callback for when a session is created.
        """
        try:
            self.logger.info(f'Session created: {sessionID}')
        except Exception as e:
            self.logger.error(f"Error in onCreate: {e}")

    def onLogon(self, sessionID: fix.SessionID) -> None:
        """
        Callback for when a logon is successful.
        """
        try:
            self.sessionID = sessionID
            self.logger.info(f'Successful logon to session {sessionID}')
        except Exception as e:
            self.logger.error(f"Error in onLogon: {e}")

    def onLogout(self, sessionID: fix.SessionID) -> None:
        """
        Callback for when a logout is successful.
        """
        try:
            self.logger.info(f'Successful logout from session {sessionID}')
        except Exception as e:
            self.logger.error(f"Error in onLogout: {e}")

    def toAdmin(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        """
        Callback for sending administrative messages.
        """
        try:
            msgType = fix.MsgType()
            message.getHeader().getField(msgType)
            if msgType.getValue() == fix.MsgType_Logon:
                message.setField(fix.RawData(self.raw_data))
                message.setField(fix.RawDataLength(len(self.raw_data)))
            self.logger.debug(f'toAdmin: {self.format_fix_message(message)}')
            self.log_message_raw(message)
        except Exception as e:
            self.logger.error(f"Error in toAdmin: {e}")

    def fromAdmin(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        """
        Callback for receiving administrative messages.
        """
        try:
            self.logger.debug(f'fromAdmin: {self.format_fix_message(message)}')
            self.log_message_raw(message)
        except Exception as e:
            self.logger.error(f"Error in fromAdmin: {e}")

    def toApp(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        """
        Callback for sending application-level messages.
        """
        try:
            self.logger.debug(f'toApp: {self.format_fix_message(message)}')
            self.log_message_raw(message)
        except Exception as e:
            self.logger.error(f"Error in toApp: {e}")

    def fromApp(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        """
        Callback for receiving application-level messages.
        """
        try:
            msgType = fix.MsgType()
            message.getHeader().getField(msgType)
            self.logger.info(f'fromApp: {self.format_fix_message(message)}')
            if msgType.getValue() == fix.MsgType_ExecutionReport:
                self.process_execution_report(message)
            else:
                self.logger.info(f'Received message: {self.format_fix_message(message)}')
            self.log_message_raw(message)
        except Exception as e:
            self.logger.error(f"Error in fromApp: {e}")

    def process_execution_report(self, message: fix.Message) -> None:
        """
        Processes Execution Report messages.
        """
        try:
            exec_id = fix.ExecID()
            symbol = fix.Symbol()
            side = fix.Side()
            order_qty = fix.OrderQty()
            last_px = fix.LastPx()
            last_qty = fix.LastQty()
            transact_time = fix.TransactTime()
            exec_type = fix.ExecType()
            ord_status = fix.OrdStatus()

            message.getField(exec_id)
            message.getField(symbol)
            message.getField(side)
            message.getField(order_qty)
            message.getField(last_px)
            message.getField(last_qty)
            message.getField(transact_time)
            message.getField(exec_type)
            message.getField(ord_status)

            log_message = (
                f"Execution Report: ExecID={exec_id.getValue()}, "
                f"Symbol={symbol.getValue()}, Side={side.getValue()}, "
                f"OrderQty={order_qty.getValue()}, LastPx={last_px.getValue()}, "
                f"LastQty={last_qty.getValue()}, TransactTime={transact_time.getValue()}, "
                f"ExecType={exec_type.getValue()}, OrdStatus={ord_status.getValue()}"
            )

            self.logger.info(log_message)
            self.log_to_file(log_message)
        except Exception as e:
            self.logger.error(f"Error processing execution report: {e}")

    def log_message_raw(self, message: fix.Message) -> None:
        """
        Logs the raw FIX message to the session and communal log files.
        
        Args:
            message (fix.Message): The FIX message to log.
        """
        try:
            raw_message = message.toString() + '\n'
            self.session_message_log.write(raw_message)
            self.session_message_log.flush()
            self.communal_message_log.write(raw_message)
            self.communal_message_log.flush()
        except Exception as e:
            self.logger.error(f"Error logging raw message: {e}")

    def log_to_file(self, message: str) -> None:
        """
        Logs the message to a file.
        """
        try:
            log_date = datetime.now().strftime("%Y-%m-%d")
            session_log_filename = f"human_readable_logs/{log_date}_execution_reports.log"
            communal_log_filename = "human_readable_logs/communal_execution_reports.log"
            os.makedirs(os.path.dirname(session_log_filename), exist_ok=True)
            with open(session_log_filename, 'a') as f:
                f.write(message + '\n')
            with open(communal_log_filename, 'a') as communal_file:
                communal_file.write(message + '\n')
        except Exception as e:
            self.logger.error(f"Error logging message to file: {e}")
