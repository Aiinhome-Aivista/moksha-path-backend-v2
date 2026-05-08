from controllers.common.auth.auth import  send_ui_otp_v4, verify_and_login_v4, select_profile_v4, login_logout_user,get_users_by_token_contact

def register_auth_routes(app):
    AUTH_URL = '/api/v1/auth'
    AUTH_LOGIN_URL = '/api/v1/auth/login'

    #Otp send
    @app.route(AUTH_URL + '/send_ui_otp_v4', methods=["POST"])
    def send_ui_otp_v4_route():
        return send_ui_otp_v4()

    #Verify and login
    @app.route(AUTH_URL + '/verify_account', methods=["POST"])
    def verify_account_get_profiles_route():
        return verify_and_login_v4()

    #Select profile
    @app.route(AUTH_URL + '/select_profile', methods=["POST"])
    def select_profile_route():
        return select_profile_v4()


    #Get users by token 
    @app.route(AUTH_URL + '/get_users_by_token_contact', methods=["GET"])
    def get_users_by_token_contact_route():
        return get_users_by_token_contact()


    #Logout
    @app.route(AUTH_LOGIN_URL + '/logout', methods=["POST"])
    def login_logout_user_route():
        return login_logout_user()