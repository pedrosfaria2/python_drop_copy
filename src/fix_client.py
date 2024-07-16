from datetime import datetime
import time
import quickfix as fix
import quickfix44 as fix44
from .fix_application import FIXApplication
import configparser


class FIXClient:
    def __init__(self, config_file_path: str, fix_application: FIXApplication):
        self.settings = fix.SessionSettings(config_file_path)
        self.application = fix_application
        self.storeFactory = fix.FileStoreFactory(self.settings)
        self.logFactory = fix.FileLogFactory(self.settings)
        self.initiator = fix.SocketInitiator(self.application, self.storeFactory, self.settings, self.logFactory)
        self.session_id = self._get_session_id_from_config(config_file_path)

    def _get_session_id_from_config(self, config_file_path: str) -> fix.SessionID:
        config = configparser.ConfigParser()
        config.read(config_file_path)
        return fix.SessionID(
            config['SESSION']['BeginString'],
            config['SESSION']['SenderCompID'],
            config['SESSION']['TargetCompID'],
        )

    def _get_session_info(self, field_name: str) -> str:
        session_settings = self.settings.get(self.session_id)
        return session_settings.getString(field_name) if session_settings.has(field_name) else 'SESSION'

    def _create_header(self, msg: fix.Message, msg_type: str) -> None:
        header = msg.getHeader()
        header.setField(fix.BeginString(fix.BeginString_FIX44))
        header.setField(fix.MsgType(msg_type))
        
        sender_comp_id = self._get_session_info('SenderCompID')
        target_comp_id = self._get_session_info('TargetCompID')
        
        header.setField(fix.SenderCompID(sender_comp_id))
        header.setField(fix.TargetCompID(target_comp_id))
        
        transact_time = datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        header.setField(fix.StringField(60, transact_time))

    def logon(self) -> None:
        self.initiator.start()
        while not self.initiator.isLoggedOn():
            time.sleep(1)

    def logout(self) -> None:
        self.initiator.stop()

    def _send_message(self, msg: fix.Message) -> None:
        sender_comp_id = self._get_session_info('SenderCompID')
        target_comp_id = self._get_session_info('TargetCompID')
        
        fix.Session.sendToTarget(msg, sender_comp_id, target_comp_id)

    def _add_party_ids(self, msg: fix.Message) -> None:
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

    def send_resend_request(self, begin_seq_no: int, end_seq_no: int) -> None:
        """
        Envia uma mensagem ResendRequest para solicitar o reenvio de mensagens.

        :param begin_seq_no: Número de sequência inicial para o reenvio.
        :param end_seq_no: Número de sequência final para o reenvio. Use 0 para solicitar todas as mensagens subsequentes.
        """
        resend_request = fix44.ResendRequest()
        resend_request.setField(fix.BeginSeqNo(begin_seq_no))
        resend_request.setField(fix.EndSeqNo(end_seq_no))

        self._send_message(resend_request)
        print(f"ResendRequest enviado de {begin_seq_no} até {end_seq_no}")

