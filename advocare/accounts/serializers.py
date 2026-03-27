from rest_framework import serializers
from users.models import User
from profiles.models import ClientProfile, LawfirmProfile, AdminProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # Client fields
    phone = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)

    # Law firm fields
    firm_name = serializers.CharField(required=False, allow_blank=True)
    registration_no = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.IntegerField(required=False, allow_null=True)
    specialization = serializers.CharField(required=False, allow_blank=True)

    # Admin fields
    secret_key = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'role',
                  'phone', 'city',
                  'firm_name', 'registration_no', 'experience', 'specialization',
                  'secret_key']

    def validate(self, data):
        role = data.get('role')
        # Conditional validation based on role
        if role == 'client':
            if not data.get('phone'):
                raise serializers.ValidationError({"phone": "Phone is required for clients."})
            if not data.get('city'):
                raise serializers.ValidationError({"city": "City is required for clients."})
        elif role == 'lawfirm':
            required_fields = ['firm_name', 'registration_no', 'experience', 'specialization']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field} is required for law firms."})
            # Experience must be positive integer
            exp = data.get('experience')
            if exp is not None and exp < 0:
                raise serializers.ValidationError({"experience": "Experience must be a positive number."})
        elif role == 'admin':
            if not data.get('secret_key'):
                raise serializers.ValidationError({"secret_key": "Secret key is required for admin."})
            # Optionally check secret key against a predefined value or a model
            # if data['secret_key'] != 'your_secret':
            #     raise serializers.ValidationError({"secret_key": "Invalid secret key."})
        return data

    def create(self, validated_data):
        # Extract profile fields
        phone = validated_data.pop('phone', None)
        city = validated_data.pop('city', None)
        firm_name = validated_data.pop('firm_name', None)
        registration_no = validated_data.pop('registration_no', None)
        experience = validated_data.pop('experience', None)
        specialization = validated_data.pop('specialization', None)
        secret_key = validated_data.pop('secret_key', None)

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create profile based on role
        role = user.role
        if role == 'client':
            ClientProfile.objects.create(
                user=user,
                phone=phone or '',
                city=city or '',
                is_onboarded=False,      # profile is complete
                status='pending'        # waiting for admin approval
            )
        elif role == 'lawfirm':
            LawfirmProfile.objects.create(
                user=user,
                firm_name=firm_name or '',
                phone=phone or '',
                registration_no=registration_no or '',
                experience=experience or 0,
                specialization=specialization or '',
                is_onboarded=False,
                status='pending'
            )
        elif role == 'admin':
            # AdminProfile doesn't have is_onboarded or status; we'll just set secret_key_verified
            AdminProfile.objects.create(
                user=user,
                phone=phone or '',
                secret_key_verified=True   # if secret key matches, otherwise you can validate first
            )
            # If you want to verify the secret key, do it before creation

        return user