from controllers.teacher.dashboard_kpis.teacher_dashboard_vw import teacher_full_dashboard
from controllers.teacher.addaptive_assesment import create_adaptive_set



def register_teacher_routes(app):
    TEACHER_URL = '/api/v1/teacher'


    # create addaptive set

    @app.route(TEACHER_URL + '/assessment/create_adaptive_set', methods=["POST"])
    def create_adaptive_set_route():
        return create_adaptive_set()



    # teacher dashboard kpis

    @app.route(TEACHER_URL + '/dashboard', methods=['GET'])
    def teacher_dashboard_kpi_route():
        return teacher_full_dashboard()




    # study meterial