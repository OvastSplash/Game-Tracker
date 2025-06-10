from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .services import SteamService

class AuthSteamID(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, steam_id):
        user = request.user
        steam_id, success = SteamService.resolve_and_update_steam_id(user, steam_id)
        if success:
            return Response({"steam_id": steam_id}, status=200)
        
        return Response({"error": "Failed to resolve vanity URL"}, status=400)
