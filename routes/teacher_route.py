from utils import api_response
from controllers.teacher.study_meterial.upload_study_meterial import upload_study_material
from controllers.teacher.study_meterial.get_teacher_study_meterial import get_teacher_study_material
from controllers.teacher.dashboard_kpis.teacher_dashboard_vw import teacher_full_dashboard
from controllers.teacher.addaptive_assesment import create_adaptive_set



def register_teacher_routes(app):
    LEARNING = '/api/v1/learning'
    PARENT_TEACHER_URL = '/api/v1/parent_teacher'



    # create addaptive set

    @app.route(LEARNING + '/assessment/create_adaptive_set', methods=["POST"])
    def create_adaptive_set_route():
        return create_adaptive_set()



    # teacher dashboard kpis

    @app.route(LEARNING + "/teacher_dashboard_vw", methods=["GET"])
    def teacher_dashboard_vw_route():
        return teacher_full_dashboard()




    # get study meterial
    
    @app.route(PARENT_TEACHER_URL + "/get_teacher_study_material", methods=["GET"])
    def get_teacher_study_material_route():
        return get_teacher_study_material()


    # upload study material
    
    @app.route(PARENT_TEACHER_URL + "/upload_study_material", methods=["POST"])
    def upload_study_material_route():
        return upload_study_material()





    # learning planner for teacher 
