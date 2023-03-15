import logging
import time

from odoo import models, fields, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class CheckboxPosSession(models.Model):
    _inherit = 'pos.session'

    kw_checkbox_shift_ids = fields.One2many(
        comodel_name='kw.checkbox.shift', inverse_name='pos_session_id', )

    def kw_checkbox_get_shift(self, organization):
        self.ensure_one()
        for s in self.kw_checkbox_shift_ids:
            if organization.id == s.cashier_id.organization_id.id:
                return s
        return False

    def action_pos_session_closing_control(self):
        for pos_session in self:
            for shift in pos_session.kw_checkbox_shift_ids:
                shift.update_info()
                if shift.status == 'OPENED':
                    try:
                        shift.close_opened()
                        shift.update_info()
                    except Exception as e:
                        _logger.debug(e)
        return super(
            CheckboxPosSession, self).action_pos_session_closing_control()

    def action_pos_session_open(self):
        _logger.info('START')
        if self.env.uid == SUPERUSER_ID:
            return False
        for pos_session in self.filtered(lambda x: not x.rescue):
            _logger.info(pos_session.config_id.kw_checkbox_cash_register_ids)
            for register in \
                    pos_session.config_id.kw_checkbox_cash_register_ids:
                _logger.info(register)
                register.update_info()
                if register.current_shift_id:
                    if register.current_shift_id.cashier_id.id not in \
                            self.env.user.kw_checkbox_cashier_ids.ids:
                        raise ValueError(_(
                            'This cash register user by other user'))
                    register.current_shift_id.pos_session_id = pos_session.id
                    continue
                cashier = self.env['kw.checkbox.cashier'].search([
                    ('id', 'in', self.env.user.kw_checkbox_cashier_ids.ids),
                    ('organization_id', '=', register.organization_id.id),
                ], limit=1)
                if not cashier:
                    raise ValueError(_(
                        'There is no valid cashier for cash register'))
                is_checkbox_online = register.ping_tax_service()
                if is_checkbox_online:
                    shift = self.env['kw.checkbox.shift'].create({
                        'cashier_id': cashier.id,
                        'cash_register_id': register.id,
                        'pos_session_id': pos_session.id, })
                    while shift.status != 'OPENED':
                        time.sleep(1)
                        shift.update_info_by_token(
                            cashier.get_checkbox().access_token)
                    register.count_offline_codes = \
                        len(self.env['kw.checkbox.offline.code'].search(
                            [('cash_register_id', '=', register.id)]).ids)
                    if not register.count_offline_codes \
                            or register.count_offline_codes \
                            < register.min_count_codes:
                        # register.go_online()
                        if not register.is_offline:
                            register.ask_offline_codes()
                        register.get_offline_codes()
                    pos_session.config_id.check_and_sell_offline_orders(
                        register)
            # if not pos_session.kw_checkbox_shift_ids.filtered(
            #         lambda x: x.status == 'OPENED'):
            #     return
        return super().action_pos_session_open()
