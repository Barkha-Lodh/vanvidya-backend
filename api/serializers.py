from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Plant, Disease, Logbook, Reminder, Admin


# ==========================================
# USER SERIALIZER
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ==========================================
# USER PROFILE SERIALIZER
# ==========================================
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


# ==========================================
# DISEASE SERIALIZER
# ==========================================
class DiseaseSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(
        source='plant.common_name',
        read_only=True
    )

    class Meta:
        model = Disease
        fields = '__all__'


# ==========================================
# PLANT SERIALIZER (Full Details)
# ==========================================
class PlantSerializer(serializers.ModelSerializer):
    diseases = DiseaseSerializer(many=True, read_only=True)
    disease_count = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = '__all__'

    def get_disease_count(self, obj):
        return obj.diseases.count()


# ==========================================
# PLANT LIST SERIALIZER (Lightweight for list view)
# ==========================================
class PlantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            'id',
            'common_name',
            'scientific_name',
            'hindi_name',
            'plant_type',
            'size',
            'toxicity',
            'edibility',
            'image_url',
            'is_common'
        ]


# ==========================================
# LOGBOOK SERIALIZER
# ==========================================
class LogbookSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(
        source='plant.common_name',
        read_only=True
    )
    plant_hindi_name = serializers.CharField(
        source='plant.hindi_name',
        read_only=True
    )
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Logbook
        fields = '__all__'


# ==========================================
# REMINDER SERIALIZER
# ==========================================
class ReminderSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(
        source='plant.common_name',
        read_only=True
    )
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Reminder
        fields = '__all__'


# ==========================================
# ADMIN SERIALIZER (Password Hidden!)
# ==========================================
class AdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Admin
        fields = [
            'id',
            'user',
            'username',
            'email',
            'name',
            'role',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


# ==========================================
# USER REGISTRATION SERIALIZER
# ==========================================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_no = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'phone_no',
            'first_name',
            'last_name'
        ]

    def create(self, validated_data):
        phone_no = validated_data.pop('phone_no')
        # create_user automatically hashes the password
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, phone_no=phone_no)
        return user