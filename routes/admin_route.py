from controllers.institute_admin.dashboard_kpis.principal_dashboard_vw import principal_dashboard_kpi
from controllers.institute_admin.bulk_upload.bulk_teacher_upload_controller_v2 import bulk_upload_users_controller_v2
def register_admin_routes(app):
    INSTITUTE_ADMIN_URL = '/api/v1/institute_admin'

    #Bulk Upload
    @app.route(INSTITUTE_ADMIN_URL + "/bulk_upload_users", methods=["POST"])
    def bulk_upload_teachers_route():
        return bulk_upload_users_controller_v2()

    #Dashboard kpis
    @app.route(INSTITUTE_ADMIN_URL + '/dashboard', methods=['GET'])
    def principal_dashboard_kpi_route():
        return principal_dashboard_kpi()