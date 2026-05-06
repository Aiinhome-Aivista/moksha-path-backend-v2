from controllers.common.auth.auth import  send_ui_otp_v4, verify_and_login_v4, select_profile_v4, login_logout_user,get_users_by_token_contact

def register_auth_routes(app):
    AUTH_URL = '/api/v1/auth'

    #Otp send
    @app.route(AUTH_URL + '/send-otp', methods=['POST'])
    def send_otp():
        return send_ui_otp_v4()

    #Verify and login
    @app.route(AUTH_URL + '/verify-and-login', methods=['POST'])
    def verify_and_login():
        return verify_and_login_v4()

    #Select profile
    @app.route(AUTH_URL + '/select-profile', methods=['POST'])
    def select_profile():
        return select_profile_v4()


    #Get users by token 
    @app.route(AUTH_URL + '/get-users-by-token-contact', methods=['POST'])
    def get_users_by_token():
        return get_users_by_token_contact()


    #Logout
    @app.route(AUTH_URL + '/logout', methods=['POST'])
    def logout():
        return login_logout_user()