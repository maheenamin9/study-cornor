from rest_framework.serializers import ModelSerializer
from base.models import Room

# Serializers in Django REST Framework are responsible for converting objects into
# data types understandable by javascript and front-end frameworks. 

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"