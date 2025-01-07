from rest_framework import serializers
from user_profile.models import User, Customization
from jwt_registration.custom_validators import password_validating


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password',
                  'password2', 'first_name', 'last_name')

    def validate(self, data):
        password = data.get('password', None)
        password2 = data.get('password2', None)

        if not password_validating(password, password2):
            raise serializers.ValidationError(
                'Please enter password correctly')

        if not data.get('first_name', None):
            raise serializers.ValidationError(
                {'error': 'First name is required.'})
        if not data.get('last_name', None):
            raise serializers.ValidationError(
                {'error': 'Last name is required.'})

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


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        password2 = data.get('password2', None)
        email = data.get('email', None)

        if not password_validating(password, password2):
            raise serializers.ValidationError(
                'Please enter password correctly')

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email was not find')

        return data


class EmailVerifySerializer(SetNewPasswordSerializer):
    def validate(self, data):
        data = super().validate(data)
        if User.objects.get(email=data['email']).email_verified:
            raise serializers.ValidationError('Email is already verified')

        return data


class EmailUpdateSerializer(serializers.ModelSerializer):
    new_email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('new_email', 'password', 'password2')

    def validate(self, data):
        new_email = data.get('new_email', None)
        password = data.get('password', None)
        password2 = data.get('password2', None)
        if not password_validating(password, password2):
            raise serializers.ValidationError(
                'Please enter password correctly')
        if User.objects.filter(email=new_email).exists():
            raise serializers.ValidationError('Email already exists')

        return data

    def update(self, user, validated_data):
        if not user.check_password(validated_data['password']):
            raise serializers.ValidationError('Password incorrect')

        user.email = validated_data['new_email']
        user.email_verified = False
        user.save()
        return user
