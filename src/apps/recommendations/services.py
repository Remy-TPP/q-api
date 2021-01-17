import requests

from decouple import config


REMY_RS_BASE_URL = config('REMY_RS_BASE_URL')


class RemyRSService:
    class RecSysException(RuntimeError):
        pass

    @staticmethod
    def get_recommendations_for_user(profile_id, n=10):
        if n == 'all':
            n = 0
        rs_response = requests.get(
            f'{REMY_RS_BASE_URL}/recommendations/user/{profile_id}',
            params={'n': n},
        )
        if rs_response.status_code != 200:
            raise RemyRSService.RecSysException(
                f'Failed to get recommendations for user from RS: {rs_response.status_code}, {rs_response.json()}')
        return rs_response.json()['predictions']

    @staticmethod
    def get_predicted_rating_for_interaction(profile_id, recipe_id):
        rs_response = requests.get(
            f'{REMY_RS_BASE_URL}/recommendations/user/{profile_id}/recipe/{recipe_id}',
        )
        if rs_response.status_code != 200:
            raise RemyRSService.RecSysException(
                f'Failed to get predicted rating from RS: {rs_response.status_code}, {rs_response.json()}')
        return rs_response.json()['prediction']
