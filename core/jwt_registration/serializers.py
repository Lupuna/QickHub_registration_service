from rest_framework import serializers

from user_profile.models import User, Customization


class UserImportantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name')
        read_only_fields = ('first_name', 'last_name')

    def validate(self, attrs):
        data = super().validate(attrs)
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password and password2 and password != password2:
            raise serializers.ValidationError('Password mismatch')
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        Customization.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password2')
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password'): instance.set_password(validated_data['password'])
        instance.save()
        return instance
