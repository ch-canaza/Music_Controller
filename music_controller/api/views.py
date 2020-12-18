from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.


class RoomView(generics.ListAPIView):
    """
        class that show room
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    """ class that defines methods to get rooms by code
    """
    serializer_class = RoomSerializer
    lookup_url_kwargs = 'code'

    def get(self, request, format=None):
        """
            methodt that obtains info about room
            * .GET information about url
            * .get parameters in that url matching 'code'
            * look for the room with that code
            * get the room and serializes
        """
        code = request.GET.get(self.lookup_url_kwargs)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data  
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Rquest': 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    """ class that allows us to join a room
    """
    
    lookup_url_kwargs = 'code'
    def post(self, request, format=None):
        """
            method that verifies the session to allow joinni a room
            * if the session does not exists, it is created
            * if the code exists look for that room
        """

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwargs)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code # this user in the current session is in this room
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)
            
            return Response({'Room not found!': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomView(APIView):
    """ class that allows creation of new rooms """
    serializer_class = CreateRoomSerializer
    
    def post(self, request, format=None):
        """
            method that defines a post method that creates new rooms
            * if a session does not exist create it 
            * serializes all data, validate it  and create the room
            * if a session already exists do not crerate a new room but update it
        """
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code # this user in the current session is in this room
                
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code # this user in the current session is in this room
                
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)


class UserInRoom(APIView):
    """ class that give us info about actual room user in in
    """
    def get(self, request, format=None):
        """
            method that returns the code where the user is 
        """
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    """ class that alow a user leaves a session
    """

    def post(self, request, format=None):
        """
            method that deletes a session 
            * remove code from user session
            * if is hosting a room delete it
            * 
        """
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)
