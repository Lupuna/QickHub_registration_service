from rest_framework import serializers
from user_profile.models import User, Link, Customization
from rest_framework.exceptions import MethodNotAllowed


class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ('id', 'title', 'link')
        read_only_fields = ('id', )


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = ('id', 'color_scheme', 'font_size')
        read_only_fields = ('id',)


class ProfileUserSerializer(serializers.ModelSerializer):
    image_identifier = serializers.CharField(read_only=True)
    links = LinkSerializer(many=True, required=False)
    customization = CustomizationSerializer(required=False)
    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'image_identifier', 'email', 'username',
            'phone', 'city', 'birthday',
            'links', 'customization'
        )

    def create(self, validated_data):
        raise MethodNotAllowed('POST', detail='Creation is not allowed using this serializer.')

    def update(self, instance, validated_data):
        links_data = validated_data.pop('links', [])
        customization_data = validated_data.pop('customization', None)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.birthday = validated_data.get('birthday', instance.birthday)
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