from GameTracker.settings import STEAM_API_TOKEN
import requests

class SteamService:
    """Сервис для работы с Steam"""
    
    @staticmethod
    def resolve_vanity_url(vanity_url):
        """
        Получает Steam ID по vanity URL
        
        Args:
            vanity_url (str): Vanity URL пользователя
            
        Returns:
            str или None: Steam ID или None, статус
        """
        try:
            params = {
                'key': STEAM_API_TOKEN,
                'vanityurl': vanity_url,
            }
            response = requests.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/", params=params)
            data = response.json()
            
            if response.status_code == 200:
                steam_id = data['response']['steamid']
                return steam_id, True
            else:
                return None, False
            
        except requests.RequestException:
            return None, False
        
    @staticmethod
    def update_user_steam_id(user, steam_id):
        """
        Обновляет Steam ID пользователя
        
        Args:
            user: Объект пользователя
            steam_id (str): Steam ID пользователя
        """
        
        user.steam_id = steam_id
        user.save()
    
    @staticmethod
    def resolve_and_update_steam_id(user, vanity_url):
        """
        Получает и обновляет Steam ID для пользователя
        
        Args:
            user: Объект пользователя
            vanity_url (str): Steam имя для конвертации
            
        Returns:
            tuple: (steam_id или None, success: bool)
        """
        if user.steam_id and len(str(user.steam_id)) == 17:
            return user.steam_id, True
        
        steam_id, success = SteamService.resolve_vanity_url(vanity_url)
        
        if success:
            SteamService.update_user_steam_id(user, steam_id)
            return steam_id, True
        
        return None, False
    
    @staticmethod
    def get_user_steam_games(user, user_games):
        """
        Получает игры пользователя из Steam
        
        Args:
            user: Объект пользователя
            user_games: Список игр пользователя
            
        Returns:
            tuple: (Список игр, success: bool)
        """
        
        if not user.steam_id:
            return [], False
        
        params = {
            'key': STEAM_API_TOKEN,
            'steamid': user.steam_id,
            'format': 'json',
            'include_appinfo': 1,
            'include_played_free_games': 1,
        }
        
        response = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                steam_games = data['response']['games'] 
                return steam_games, True
        return [], False
    
    @staticmethod
    def get_user_playtime(user_games, steam_games):
        """
        Получает время игры пользователя из Steam
        
        Args:
            user_games: Список игр пользователя
            steam_games: Список игр из Steam
            
        Returns:
            tuple: (Словарь игр и их время, общее время в часах)
        """
        
        sortedGames = {}
        hours_total = 0
        
        for game in steam_games:
            steam_game_name = game['name']
                    
            if steam_game_name.lower() in (name.lower() for name in user_games):
                time_in_minutes = game['playtime_forever']
                hours_decimal = round(time_in_minutes / 60, 1)
                hours_total += hours_decimal
                formatted_time = f"{hours_decimal} ч."
                sortedGames[steam_game_name] = formatted_time
                
        return sortedGames, int(hours_total)