# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage

FILEPOND_UPLOAD_TMP = getattr(settings, 'DJANGO_DRF_FILEPOND_UPLOAD_TMP',
                        os.path.join(settings.BASE_DIR,'filepond_uploads'))
storage = FileSystemStorage(location=FILEPOND_UPLOAD_TMP)

LOG = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TemporaryUpload(models.Model):
    
    FILE_DATA = 'F'
    URL = 'U'
    UPLOAD_TYPE_CHOICES = (
        (FILE_DATA, 'Uploaded file data'),
        (URL, 'Remote file URL'),
    )
    
    file_id = models.CharField(primary_key=True, max_length=22, 
                               validators=[MinLengthValidator(22)])
    file = models.FileField(storage=storage)
    upload_name = models.CharField(max_length=512)
    uploaded = models.DateTimeField(auto_now_add=True)
    upload_type = models.CharField(max_length = 1, 
                                   choices=UPLOAD_TYPE_CHOICES)

# When a TemporaryUpload record is deleted, we need to delete the 
# corresponding file from the filesystem by catching the post_delete signal.
@receiver(post_delete, sender=TemporaryUpload)
def delete_temp_upload_file(sender, instance, **kwargs):
    # Check that the file parameter for the instance is not None
    # and that the file exists and is not a directory! Then we can delete it
    LOG.debug("*** post_delete signal handler called. Deleting file.")
    if instance.file:
        if (os.path.exists(instance.file.path) and 
            os.path.isfile(instance.file.path)):
            os.remove(instance.file.path)