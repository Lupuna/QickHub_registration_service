from django.core.files import File
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed, ValidationError

from user_profile.models import User, Link, Customization
from user_profile.tasks import upload_file


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('id', 'title', 'link')
        read_only_fields = ('id',)


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = ('id', 'color_scheme', 'font_size')
        read_only_fields = ('id',)


class ProfileUserSerializer(serializers.ModelSerializer):
    image_identifier = serializers.CharField(read_only=True)
    links = LinkSerializer(many=True, required=False)
    customization = CustomizationSerializer(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'image_identifier',
            'phone', 'city', 'birthday',
            'links', 'customization', 'first_name', 'last_name'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        raise MethodNotAllowed('POST', detail='Creation is not allowed using this serializer.')

    def update(self, instance, validated_data):
        links_data = validated_data.pop('links', [])
        customization_data = validated_data.pop('customization', None)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        if customization_data:
            customization = instance.customization
            for attr, value in customization_data.items():
                setattr(customization, attr, value)
            customization.save()

        links_title = instance.links.all().values_list('title', flat=True)
        for link_data in links_data:
            if link_data['title'] in links_title:
                Link.objects.filter(title=link_data['title']).update(**link_data)
            else:
                Link.objects.create(user=instance, **link_data)
        return instance


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, write_only=True)
    user = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        image = validated_data['image']
        user = validated_data['user']

        try:
            photo_uuid = User.objects.get(id=user).image_identifier
        except User.DoesNotExist as error:
            raise ValidationError(error)

        storage = FileSystemStorage()
        image_name = f'{photo_uuid}.{image.name.split(".")[-1]}'
        storage.save(image_name, File(image))
        upload_file.delay(storage.path(image_name))
        return {'status': True}
