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
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_filename = f"human_readable_logs/{log_date}_fix.log"
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)

        handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def onCreate(self, sessionID: fix.SessionID) -> None:
        self.logger.info(f'Session created: {sessionID}')

    def onLogon(self, sessionID: fix.SessionID) -> None:
        self.sessionID = sessionID
        self.logger.info(f'Successful logon to session {sessionID}')    

    def onLogout(self, sessionID: fix.SessionID) -> None:
        self.logger.info(f'Successful logout from session {sessionID}')

    def toAdmin(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Logon:
            message.setField(fix.RawData(self.raw_data))
            message.setField(fix.RawDataLength(len(self.raw_data)))
        self.logger.debug(f'toAdmin: {message.toString()}')

    def fromAdmin(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        self.logger.debug(f'fromAdmin: {message.toString()}')

    def toApp(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        self.logger.debug(f'toApp: {message.toString()}')

    def fromApp(self, message: fix.Message, sessionID: fix.SessionID) -> None:
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_ExecutionReport:
            self.process_execution_report(message)
        else:
            self.logger.info(f'Received message: {message.toString()}')

    def process_execution_report(self, message: fix.Message) -> None:
        exec_id = fix.ExecID()
        symbol = fix.Symbol()
        side = fix.Side()
        order_qty = fix.OrderQty()
        last_px = fix.LastPx()
        last_qty = fix.LastQty()
        transact_time = fix.TransactTime()

        message.getField(exec_id)
        message.getField(symbol)
        message.getField(side)
        message.getField(order_qty)
        message.getField(last_px)
        message.getField(last_qty)
        message.getField(transact_time)

        log_message = (
            f"Execution Report: ExecID={exec_id.getValue()}, "
            f"Symbol={symbol.getValue()}, Side={side.getValue()}, "
            f"OrderQty={order_qty.getValue()}, LastPx={last_px.getValue()}, "
            f"LastQty={last_qty.getValue()}, TransactTime={transact_time.getValue()}"
        )
        self.logger.info(log_message)
        self.log_to_file(log_message)

    def log_to_file(self, message: str) -> None:
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_filename = f"human_readable_logs/{log_date}_execution_reports.log"
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        with open(log_filename, 'a') as f:
            f.write(message + '\n')
