# cases/serializers.py
from rest_framework import serializers
from .models import Case, CourtUpdate
from profiles.models import TeamMember

class CaseSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    client_id = serializers.IntegerField(source='client.id', read_only=True)
    class Meta:
        model = Case
        fields = '__all__'

class CourtUpdateSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_id = serializers.IntegerField(source='case.id', read_only=True)
    client_id = serializers.IntegerField(source='case.client.id', read_only=True)
    client_name = serializers.CharField(source='case.client.full_name', read_only=True)
    
    class Meta:
        model = CourtUpdate
        fields = '__all__'

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'