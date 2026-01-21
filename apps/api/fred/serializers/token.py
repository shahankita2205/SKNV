"""
Token Serializers and Services
"""

import logging
import secrets
from typing import Optional

from django.db import transaction
from rest_framework import serializers

from fred.models.models import Token

logger = logging.getLogger(__name__)


class TokenErrorCodes:
    ERROR_TOKEN_NOT_FOUND = 23001
    ERROR_UNABLE_CREATE_TOKEN = 23002
    ERROR_TOKEN_EXPIRED = 23003
    ERROR_TOKEN_INVALID = 23004


class TokenServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = "__all__"


class TokenService:

    @staticmethod
    def generate_token(length: int = 8) -> str:
        return secrets.token_urlsafe(length)[:length]

    @staticmethod
    def create(
        token_type: str, record_type: str, record_id: int, amount: float = None
    ) -> str:
        try:
            token_value = TokenService.generate_token(8)

            with transaction.atomic(using="fred"):
                token = Token()
                token.token = token_value
                token.status = "active"
                token.type = token_type
                token.recordtype = record_type
                token.recordid = record_id
                if amount is not None:
                    token.amount = amount
                token.save(using="fred")

                logger.info(
                    f"Token created: type={token_type}, record={record_type}:{record_id}"
                )
                return token_value
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            raise TokenServiceException(
                "Unable to create token", TokenErrorCodes.ERROR_UNABLE_CREATE_TOKEN
            )

    @staticmethod
    def get_by_token(token_value: str) -> Optional[Token]:
        try:
            return Token.objects.using("fred").get(token=token_value, status="active")
        except Token.DoesNotExist:
            return None

    @staticmethod
    def validate_token(token_value: str, token_type: str = None) -> Token:
        token = TokenService.get_by_token(token_value)

        if not token:
            raise TokenServiceException(
                "Token not found or expired", TokenErrorCodes.ERROR_TOKEN_NOT_FOUND
            )

        if token.status != "active":
            raise TokenServiceException(
                "Token has been used or expired", TokenErrorCodes.ERROR_TOKEN_EXPIRED
            )

        if token_type and token.type != token_type:
            raise TokenServiceException(
                f"Invalid token type: expected {token_type}",
                TokenErrorCodes.ERROR_TOKEN_INVALID,
            )

        return token

    @staticmethod
    def invalidate_token(token_value: str) -> bool:
        try:
            token = Token.objects.using("fred").get(token=token_value)
            token.status = "used"
            token.save(using="fred")
            logger.info(f"Token invalidated: {token_value}")
            return True
        except Token.DoesNotExist:
            return False

    @staticmethod
    def create_password_reset_token(user_id: int) -> str:
        return TokenService.create(
            token_type="password", record_type="user", record_id=user_id
        )

    @staticmethod
    def send_password_new_user(email: str, token: str, realm: str = "default") -> bool:
        logger.info(
            f"Password email would be sent to {email} with token {token} for realm {realm}"
        )
        return True


__all__ = [
    "TokenErrorCodes",
    "TokenServiceException",
    "TokenSerializer",
    "TokenService",
]
