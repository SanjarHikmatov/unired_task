from django.db import models
from django.utils.translation import gettext_lazy as _

from jsonrpcserver import Error as JsonRpcError

from apps.utils.models.base_model import BaseModel



class Error(BaseModel):
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
        return f"{self.code}: {self.en}"


class CustomError:
    def __init__(self, code, lang='en'):
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
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message
            }
        }

    def to_jsonrpc_error(self):
        return JsonRpcError(code=self.code, message=self.message)

