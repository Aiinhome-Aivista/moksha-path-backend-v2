from controllers.common.users.user_profile_details import get_user_profile ,get_academic_details , update_user_profile
from controllers.common.users.page_menu_access import get_user_menu

def register_user_routes(app):
    USER_URL = '/api/v1/user'

# page access routes

    @app.route(USER_URL + '/menu/page_acess', methods=["POST"])  # Changed from GET to POST
    def get_user_menu_route():
        return get_user_menu()

# getting user profile functions

    @app.route(USER_URL +'/profile_info', methods=['GET'])
    def fetch_profile():
        return get_user_profile()

# update profile details
#    
    @app.route(USER_URL +'/update_profile', methods=['POST'])
    def save_profile():
        return update_user_profile()

# getting academic details   
    @app.route(USER_URL +'/user_academic_info', methods=['GET'])
    def user_academic_details():
        return get_academic_details()