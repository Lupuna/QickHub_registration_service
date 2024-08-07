from rest_framework import serializers
from user_profile.models import User, Customization


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2'
        )

    def validate(self, attrs):
        data = super().validate(attrs)
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password and password2 and password != password2:
            raise serializers.ValidationError('Password mismatch')
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        Customization.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

