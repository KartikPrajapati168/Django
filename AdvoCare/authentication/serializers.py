from rest_framework import serializers
from users.models import User

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password', 'role',
            'full_name', 'phone', 'city',
            'firm_name', 'registration_no',
            'experience', 'specialization'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Check password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        role = data.get("role")

        # Role-based validation
        if role == "LAWYER":
            if not data.get("registration_no"):
                raise serializers.ValidationError({
                    "registration_no": "Registration number is required for lawyers."
                })
            if not data.get("experience"):
                raise serializers.ValidationError({
                    "experience": "Experience is required for lawyers."
                })

        return data

    def create(self, validated_data):
        # Remove confirm_password (not part of the model)
        validated_data.pop('confirm_password')
        full_name = validated_data.pop('full_name', '')

        # Split full name into first_name and last_name
        first_name = ""
        last_name = ""
        if full_name:
            name_parts = full_name.strip().split(' ', 1)
            first_name = name_parts[0]
            if len(name_parts) > 1:
                last_name = name_parts[1]

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            first_name=first_name,
            last_name=last_name,
            phone=validated_data.get('phone', ''),
            city=validated_data.get('city', ''),
            firm_name=validated_data.get('firm_name', ''),
            registration_no=validated_data.get('registration_no', ''),
            experience=validated_data.get('experience'),
            specialization=validated_data.get('specialization', '')
        )

        return user