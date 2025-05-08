from django.db.models.signals import post_delete, pre_save, m2m_changed, post_save
from django.dispatch import receiver
from api.models import *
from django.db import transaction
from api.utils import use_pusher, log_error
from api.serializer import ProfileSerializerOne, ChallengeParticipantSerializerOne
import traceback


def delete_file_from_storage(file_instance):
    storage = file_instance.url.storage
    file_path = file_instance.url.name
    if storage.exists(file_path):
        storage.delete(file_path)


# Community
@receiver(m2m_changed, sender=Community.members.through)
def update_community_on_members_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ['post_add', 'post_remove']:
        channel = f"community_{instance.id}"
        def send_data():
            pusher = use_pusher()
            change_type = 'add' if action == 'post_add' else 'remove'
            data = ProfileSerializerOne(Profile.objects.filter(id__in=pk_set), many=True).data
            try:
                pusher.trigger(channel, 'community_members_update', {'data': data, 'action': change_type})
            except Exception:
                log_error(traceback.format_exc())
                pass

        transaction.on_commit(send_data)


# Challenge Participant
@receiver(post_save, sender=ChallengeParticipant)
def challenge_participant_added(sender, instance, **kwargs):
    channel = f"community_{instance.challenge.community.id}"
    challenge_id = instance.challenge.id
    data = ChallengeParticipantSerializerOne(instance).data
    def send_data():
        try:
            pusher = use_pusher()
            pusher.trigger(channel, 'challenge_participants_update', {'data': data, 'action': 'add', 'challenge_id': challenge_id})
        except Exception:
            log_error(traceback.format_exc())
            pass

    transaction.on_commit(send_data)


@receiver(post_delete, sender=ChallengeParticipant)
def challenge_participant_removed(sender, instance, **kwargs):
    channel = f"community_{instance.challenge.community.id}"
    challenge_id = instance.challenge.id
    data = ChallengeParticipantSerializerOne(instance).data
    def send_data():
        try:
            pusher = use_pusher()
            pusher.trigger(channel, 'challenge_participants_update', {'data': data, 'action': 'remove', 'challenge_id': challenge_id})
        except Exception:
            log_error(traceback.format_exc())
            pass

    transaction.on_commit(send_data)


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

