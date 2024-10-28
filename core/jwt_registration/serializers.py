from rest_framework import serializers

from user_profile.models import User, Customization


class UserImportantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        data = super().validate(attrs)
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if self.instance is None:
            if not attrs.get('first_name'):
                raise serializers.ValidationError({'error': 'First name is required.'})
            if not attrs.get('last_name'):
                raise serializers.ValidationError({'error': 'Last name is required.'})

        if (password and password2) and password != password2:
            raise serializers.ValidationError('Password mismatch')
        attrs.pop('password2')
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        Customization.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password'): instance.set_password(validated_data['password'])
        instance.save()
        return instance
