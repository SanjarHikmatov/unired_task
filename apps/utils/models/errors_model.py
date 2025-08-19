from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonrpcserver import Error as JsonRpcError

from apps.utils.models.base_model import BaseModel


class Error(BaseModel):
    """
    Error model that stores error codes and messages in multiple languages.
    Each error has a unique numeric code and a message in English, Russian, and Uzbek.
    """

    code = models.IntegerField(
        unique=True,
        db_index=True,
        verbose_name=_("Error code"),
    )
    en = models.CharField(
        max_length=255,
        verbose_name=_("Message (EN)"),
    )
    ru = models.CharField(
        max_length=255,
        verbose_name=_("Message (RU)"),
    )
    uz = models.CharField(
        max_length=255,
        verbose_name=_("Message (UZ)"),
    )

    class Meta:
        db_table = "errors"
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")

    def __str__(self):
        """
        String representation of the error.
        Returns the code and the English message.
        """
        return f"{self.code}: {self.en}"


class CustomError:
    """
    Custom error wrapper that loads messages from the Error model
    and formats them for API or JSON-RPC responses.
    """

    def __init__(self, code, lang='en'):
        """
        Initialize a custom error.

        Args:
            code (int): Error code to look up in the database.
            lang (str): Language code ('en', 'ru', 'uz'). Defaults to 'en'.
        """
        self.code = code
        self.lang = lang

        try:
            error = Error.objects.get(code=code)

            if lang == 'uz':
                self.message = error.uz
            elif lang == 'ru':
                self.message = error.ru
            else:
                self.message = error.en

        except Error.DoesNotExist:
            self.message = "Unknown error"

    def as_dict(self):
        """
        Convert the error into a dictionary format for API responses.

        Returns:
            dict: JSON-friendly error representation.
        """
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message
            }
        }

    def to_jsonrpc_error(self):
        """
        Convert the error into a JSON-RPC error object.

        Returns:
            JsonRpcError: Compatible JSON-RPC error.
        """
        return JsonRpcError(code=self.code, message=self.message)
