from controllers.common.users.user_profile_details import get_user_profile ,get_academic_details , update_user_profile
from controllers.common.users.page_menu_access import get_user_menu

def register_user_routes(app):
    USERS_URL = '/api/v1/users'

# page access routes

    @app.route(USERS_URL + '/get-user-menu', methods=['POST'])
    def get_user_menu_page():
        return get_user_menu()

# getting user profile functions

    @app.route(USERS_URL + '/get-user-profile', methods=['POST'])
    def get_profile():
        return get_user_profile()

# update profile details   
    @app.route(USERS_URL + '/update-user-profile', methods=['POST'])
    def update_profile():
        return update_user_profile()

# getting academic details   
    @app.route(USERS_URL + '/get-academic-details', methods=['POST'])
    def get_academic_detail():
        return get_academic_details()