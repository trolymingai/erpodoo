# -*- coding: utf-8 -*-
import json
import urllib.request

from odoo import models


class MingSmsProvider(models.AbstractModel):
    _name = 'ming.sms.provider'
    _description = 'Adapter nhà cung cấp SMS Ming'

    def send_sms(self, config, phone, body):
        if not config.sms_provider or not config.sms_api_url or not config.sms_api_key:
            return {
                'success': False,
                'provider_message_id': False,
                'error_message': 'Chưa cấu hình đầy đủ nhà cung cấp SMS.',
                'raw_response': False,
            }

        payload = {
            'to': phone,
            'body': body,
            'brandname': config.sms_brandname or config.sms_sender_id or config.sms_sender_name or '',
        }
        try:
            data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            request = urllib.request.Request(
                config.sms_api_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer %s' % config.sms_api_key,
                },
            )
            raw = urllib.request.urlopen(request, timeout=12).read().decode('utf-8', 'replace')
            return {
                'success': True,
                'provider_message_id': False,
                'error_message': False,
                'raw_response': raw,
            }
        except Exception as exc:
            return {
                'success': False,
                'provider_message_id': False,
                'error_message': str(exc),
                'raw_response': False,
            }

    def send_lark(self, config, webhook, body):
        if not webhook:
            return {
                'success': False,
                'provider_message_id': False,
                'error_message': 'Chưa cấu hình webhook Lark.',
                'raw_response': False,
            }
        payload = {
            'msg_type': 'text',
            'content': {'text': body},
        }
        try:
            data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            request = urllib.request.Request(
                webhook,
                data=data,
                headers={'Content-Type': 'application/json'},
            )
            raw = urllib.request.urlopen(request, timeout=12).read().decode('utf-8', 'replace')
            return {
                'success': True,
                'provider_message_id': False,
                'error_message': False,
                'raw_response': raw,
            }
        except Exception as exc:
            return {
                'success': False,
                'provider_message_id': False,
                'error_message': str(exc),
                'raw_response': False,
            }
