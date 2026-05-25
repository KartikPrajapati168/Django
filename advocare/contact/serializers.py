# from rest_framework import serializers
# from .models import ContactMessage

# class ContactMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ContactMessage
#         fields = ['id', 'full_name', 'email', 'phone', 'subject', 'message', 'created_at', 'is_read']
#         read_only_fields = ['id', 'created_at', 'is_read']
from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    # Map frontend field 'fullName' to model field 'full_name'
    fullName = serializers.CharField(source='full_name', write_only=True)
    
    class Meta:
        model = ContactMessage
        fields = ['id', 'fullName', 'full_name', 'email', 'phone', 'subject', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'is_read', 'full_name']

    def create(self, validated_data):
        # Remove the temporary 'fullName' field if present
        validated_data.pop('fullName', None)
        return super().create(validated_data)