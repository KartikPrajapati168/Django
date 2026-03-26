from rest_framework import serializers
from users.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['full_name','email','password','role']

    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
    