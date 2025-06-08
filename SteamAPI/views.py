from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from GameTracker.settings import STEAM_API_TOKEN
import requests

# 228PUP
class AuthSteamID(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, steam_id):
        response = requests.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_TOKEN}&vanityurl={steam_id}")
        user = request.user
        
        if len(str(user.steam_id)) == 17:
            return Response(response.json(), status=200)
        
        if response.status_code == 200:
            steam_id = response.json()["response"]["steamid"]
            user.steam_id = steam_id
            user.save()
            return Response(response.json(), status=200)
        
        return Response(response.json(), status=400)
