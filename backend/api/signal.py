from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from api.models import *
from django.db import transaction


def delete_file_from_storage(file_instance):
    storage = file_instance.url.storage
    file_path = file_instance.url.name
    if storage.exists(file_path):
        storage.delete(file_path)


# User Image File
@receiver(post_delete, sender=UserImageFile)
def auto_delete_staff_image_file_post_delete(sender, instance, **kwargs):
    transaction.on_commit(lambda: delete_file_from_storage(instance))


@receiver(pre_save, sender=UserImageFile)
def auto_delete_old_staff_image_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = UserImageFile.objects.get(pk=instance.pk).url
        storage = old_file.storage
        old_file_path = old_file.name
    except UserImageFile.DoesNotExist:
        return

    def delete_old_file():
        if storage.exists(old_file_path):
            storage.delete(old_file_path)
    new_file = instance.url
    if old_file and old_file != new_file:
        transaction.on_commit(delete_old_file)

