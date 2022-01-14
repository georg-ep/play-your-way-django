from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from core import exception
from core.helpers import convert_size


def validate_file_size(value):
    filesize = value.size

    if filesize > settings.MAX_UPLOAD_SIZE:
        error_msg = _('File is bigger than max file size (%(file_size)s)') % {'file_size': convert_size(settings.MAX_UPLOAD_SIZE)}
        raise exception.get_list_error(ValidationError, error_msg)
    else:
        return value
