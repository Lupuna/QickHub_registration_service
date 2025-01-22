from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed, ValidationError

from user_profile.models import User, Link, Customization, Notifications, Reminders
from user_profile.tasks import upload_file


class LinkSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ('id', 'title', 'link')
        read_only_fields = ('id',)

    def get_title(self, obj):
        return obj.get_title_display()


class PositionForUsersInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    access_weight = serializers.CharField()
    company = serializers.IntegerField()


class DepartmentForUsersInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    parent = serializers.CharField()
    company = serializers.IntegerField()
    color = serializers.CharField()


class ProfileUserForDepSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'phone', 'business_phone', 'image_identifier', 'city',
                  'birthday', 'first_name', 'last_name', 'otchestwo', 'date_joined')


class DepartmentInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    parent = serializers.IntegerField()
    users = ProfileUserForDepSerializer(many=True)
    color = serializers.CharField()


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = ('id', 'color_scheme', 'font_size')
        read_only_fields = ('id',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = (
            'id', *(i for i in [j for j in Notifications().__dict__.keys()][3::]))
        read_only_fields = ('id',)


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminders
        fields = (
            'id', *(i for i in [j for j in Reminders().__dict__.keys()][3::]))
        read_only_fields = ('id',)


class ProfileUserSerializer(serializers.ModelSerializer):
    image_identifier = serializers.CharField(read_only=True)
    links = LinkSerializer(many=True, required=False)
    customization = CustomizationSerializer(required=False)
    reminder = ReminderSerializer(required=False)
    notification = NotificationSerializer(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'image_identifier',
            'phone', 'city', 'birthday',
            'links', 'customization', 'reminder',
            'notification', 'first_name', 'last_name',
        )
        read_only_fields = ('id',)

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        if 'links' in data:
            result['links'] = [
                {'title': link['title'], 'link': link['link']} for link in data['links']
            ]
        return result

    def create(self, validated_data):
        raise MethodNotAllowed(
            'POST', detail='Creation is not allowed using this serializer.')

    def update(self, instance, validated_data):
        links_data = validated_data.pop('links', [])
        customization_data = validated_data.get('customization', None)
        reminder_data = validated_data.get('reminder', None)
        notification_data = validated_data.get('notification', None)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.save()

        if customization_data:
            customization = instance.customization
            for attr, value in customization_data.items():
                setattr(customization, attr, value)
            customization.save()

        if reminder_data:
            reminder = instance.reminder
            for attr, val in reminder_data.items():
                setattr(reminder, attr, val)
            reminder.save()

        if notification_data:
            notification = instance.notification
            for attr, val in notification_data.items():
                setattr(notification, attr, val)
            notification.save()

        links_title = instance.links.all().values_list('title', flat=True)

        for link_data in links_data:
            if link_data['title'] in links_title:
                Link.objects.filter(
                    title=link_data['title']
                ).update(**link_data)
            else:
                Link.objects.create(user=instance, **link_data)
        return instance


class ProfileUserForCompanySerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, required=False)
    positions = PositionForUsersInfoSerializer(many=True, required=False)
    departments = DepartmentForUsersInfoSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'otchestwo', 'birthday',
            'phone', 'business_phone', 'city', 'image_identifier', 'date_joined', 'links', 'positions', 'departments',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        emails = self.context.get('emails', [])
        pos_deps = self.context.get('pos_deps', [])
        idx = emails.index(instance.email)
        representation['positions'] = pos_deps[idx][0]
        representation['departments'] = pos_deps[idx][1]

        return representation


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, write_only=True)
    user = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        image = validated_data['image']
        user = validated_data['user']

        try:
            photo_uuid = cache.get_or_set(settings.USER_PROFILE_SER_CACHE_KEY.format(
                ser='ImageSerializer', user=user), User.objects.get(id=user).image_identifier, settings.CACHE_LIVE_TIME)
        except User.DoesNotExist as error:
            raise ValidationError(error)

        storage = FileSystemStorage()
        image_name = f'{photo_uuid}.{image.name.split(".")[-1]}'
        storage.save(image_name, File(image))
        upload_file.delay(storage.path(image_name))
        return {'status': True}
