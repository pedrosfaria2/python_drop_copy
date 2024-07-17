from datetime import datetime
import time
import quickfix as fix
import quickfix44 as fix44
from .fix_application import FIXApplication
import configparser
import logging

class FIXClient:
    def __init__(self, config_file_path: str, fix_application: FIXApplication):
        """
        Initialize settings, application, store factory, log factory, and initiator.
        """
        self.config_file_path = config_file_path
        self.fix_application = fix_application
        self.settings = None
        self.application = fix_application
        self.storeFactory = None
        self.logFactory = None
        self.initiator = None
        self.session_id = None

        self._initialize_settings()

    def _initialize_settings(self) -> None:
        """
        Initialize settings from the configuration file.
        """
        try:
            self.settings = fix.SessionSettings(self.config_file_path)
            self.storeFactory = fix.FileStoreFactory(self.settings)
            self.logFactory = fix.FileLogFactory(self.settings)
            self.session_id = self._get_session_id_from_config(self.config_file_path)
        except (fix.ConfigError, fix.RuntimeError) as e:
            logging.error(f"Error initializing FIX client with config {self.config_file_path}: {e}")
            raise

    def _get_session_id_from_config(self, config_file_path: str) -> fix.SessionID:
        """
        Extract the SessionID from the configuration file.
        """
        try:
            config = configparser.ConfigParser()
            config.read(config_file_path)
            session_cfg = config['SESSION']
            return fix.SessionID(
                session_cfg['BeginString'],
                session_cfg['SenderCompID'],
                session_cfg['TargetCompID']
            )
        except KeyError as e:
            logging.error(f"Missing key in config file {config_file_path}: {e}")
            raise
        except configparser.Error as e:
            logging.error(f"ConfigParser error reading {config_file_path}: {e}")
            raise

    def logon(self) -> None:
        """
        Start the connection and wait until logon is successful.
        """
        primary_host, secondary_host = self._get_hosts()
        if self._try_logon(primary_host):
            logging.info(f"Successfully logged on using primary host: {primary_host}")
        elif secondary_host and self._try_logon(secondary_host):
            logging.info(f"Successfully logged on using secondary host: {secondary_host}")
        else:
            logging.error("Failed to logon using both primary and secondary hosts.")
            raise RuntimeError("Logon failed for both primary and secondary hosts.")

    def _get_hosts(self) -> tuple:
        """
        Retrieve primary and secondary hosts from the configuration.
        """
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        primary_host = config['SESSION'].get('SocketConnectHostPrimary')
        secondary_host = config['SESSION'].get('SocketConnectHostSecondary')
        return primary_host, secondary_host

    def _try_logon(self, host: str) -> bool:
        """
        Attempt to logon to the specified host.
        """
        try:
            self._set_socket_connect_host(host)
            self.initiator = fix.SocketInitiator(self.application, self.storeFactory, self.settings, self.logFactory)
            self.initiator.start()
            for _ in range(10):  # Try for a certain number of attempts
                if self.initiator.isLoggedOn():
                    return True
                time.sleep(1)
            self.initiator.stop()
        except fix.RuntimeError as e:
            logging.error(f"Failed to logon to host {host}: {e}")
        return False

    def _set_socket_connect_host(self, host: str) -> None:
        """
        Set the SocketConnectHost in the session settings.
        """
        try:
            session_settings = self.settings.get(self.session_id)
            session_settings.setString("SocketConnectHost", host)
        except fix.ConfigError as e:
            logging.error(f"Error setting SocketConnectHost to {host}: {e}")
            raise

    def logout(self) -> None:
        """
        Stop the connection.
        """
        try:
            self.initiator.stop()
        except fix.RuntimeError as e:
            logging.error(f"Error during logout: {e}")
            raise

    def _send_message(self, msg: fix.Message) -> None:
        """
        Send the FIX message to the target.
        """
        try:
            sender_comp_id = self._get_session_info('SenderCompID')
            target_comp_id = self._get_session_info('TargetCompID')
            fix.Session.sendToTarget(msg, sender_comp_id, target_comp_id)
        except fix.RuntimeError as e:
            logging.error(f"Error sending message: {e}")
            raise

    def _get_session_info(self, field_name: str) -> str:
        """
        Get session information based on the provided field name.
        """
        try:
            session_settings = self.settings.get(self.session_id)
            return session_settings.getString(field_name) if session_settings.has(field_name) else 'SESSION'
        except (fix.ConfigError, fix.RuntimeError) as e:
            logging.error(f"Error getting session info for {field_name}: {e}")
            raise

    def _create_header(self, msg: fix.Message, msg_type: str) -> None:
        """
        Create and set the header for the FIX message.
        """
        try:
            header = msg.getHeader()
            header.setField(fix.BeginString(fix.BeginString_FIX44))
            header.setField(fix.MsgType(msg_type))
            
            sender_comp_id = self._get_session_info('SenderCompID')
            target_comp_id = self._get_session_info('TargetCompID')
            
            header.setField(fix.SenderCompID(sender_comp_id))
            header.setField(fix.TargetCompID(target_comp_id))
            
            transact_time = datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
            header.setField(fix.StringField(60, transact_time))
        except (fix.ConfigError, fix.RuntimeError) as e:
            logging.error(f"Error creating header for message type {msg_type}: {e}")
            raise

    def send_resend_request(self, begin_seq_no: int, end_seq_no: int) -> None:
        """
        Send a ResendRequest message to request the resending of messages.

        :param begin_seq_no: Begin sequence number for the resend.
        :param end_seq_no: End sequence number for the resend. Use 0 to request all subsequent messages.
        """
        try:
            resend_request = fix44.ResendRequest()
            resend_request.setField(fix.BeginSeqNo(begin_seq_no))
            resend_request.setField(fix.EndSeqNo(end_seq_no))

            self._send_message(resend_request)
            logging.info(f"ResendRequest sent from {begin_seq_no} to {end_seq_no}")
        except (fix.ConfigError, fix.RuntimeError) as e:
            logging.error(f"Error sending ResendRequest from {begin_seq_no} to {end_seq_no}: {e}")
            raise

    def _add_party_ids(self, msg: fix.Message) -> None:
        """
        Add party IDs to the FIX message.
        """
        try:
            party_ids = [
                ('SUP', 'D', 36),
                ('93', 'D', 7),
                ('DMAPC', 'D', 54)
            ]
            for party_id, party_id_source, party_role in party_ids:
                group = fix44.NewOrderSingle.NoPartyIDs()
                group.setField(fix.PartyID(party_id))
                group.setField(fix.PartyIDSource(party_id_source))
                group.setField(fix.PartyRole(party_role))
                msg.addGroup(group)
        except (fix.ConfigError, fix.RuntimeError) as e:
            logging.error(f"Error adding party IDs: {e}")
            raise
