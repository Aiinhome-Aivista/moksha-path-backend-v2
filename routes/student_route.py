from controllers.student.study_meterial.get_study_meterial_v3 import sp_get_study_material_v3
from controllers.student.learing_planner.student_planner import get_student_dashboard_view
from controllers.student.learing_planner.student_planner import get_student_subjects_tab_info
from controllers.student.learing_planner.student_planner import get_multi_chapter_tests
from controllers.student.learing_planner.student_planner import get_student_planner_dashboard
from controllers.student.dashboard_kpis import student_subject_dashboard_vw
from controllers.student.dashboard_kpis.student_remediation_dashboard import student_remediation_ai_insights
from controllers.student.dashboard_kpis import student_remediation_dashboard
from controllers.student.dashboard_kpis import student_performance_vw
from controllers.student.adaptive_assessment.start_assessment import addaptive_start_assessment
from controllers.student.adaptive_assessment import skip_assessment_question
from controllers.student.adaptive_assessment import get_next_adaptive_question
from controllers.student.adaptive_assessment import finish_adaptive_assessment
from controllers.student.dashboard_kpis import student_mock_dashboard_vw
def register_student_routes(app):
    LEARNING = '/api/v1/learning'
    PARENT_TEACHER_URL = '/api/v1/parent_teacher'



    @app.route(LEARNING + '/assessment/addaptive_start', methods=["POST"])
    def addaptive_start_assessment_route():
        return addaptive_start_assessment()
  



    @app.route(LEARNING + '/assessment/get_next_question', methods=["GET"])
    def get_next_adaptive_question_route():
        return get_next_adaptive_question()





    @app.route(LEARNING + '/assessment/skip_assessment_question', methods=["POST"])
    def skip_assessment_question_route():
        return skip_assessment_question()




    @app.route(LEARNING + '/assessment/finish_adaptive', methods=["POST"])
    def finish_adaptive_assessment_route():
        return finish_adaptive_assessment()



    @app.route(LEARNING + "/student_mock_dashboard_vw", methods=["GET"])
    def student_mock_dashboard_vw_route():
        return student_mock_dashboard_vw()



    @app.route(LEARNING + "/student_performance_vw", methods=["GET"])
    def student_performance_vw_route(): 
        return student_performance_vw()




    @app.route(LEARNING + "/student_remediation_dashboard", methods=["GET"])
    def student_remediation_dashboard_route():
        return student_remediation_dashboard()



    @app.route(LEARNING + "/student_remediation_ai_insights", methods=["GET"])
    def student_remediation_ai_insights_route():
        return student_remediation_ai_insights()



    @app.route(LEARNING + "/student_subject_dashboard_vw", methods=["GET"])
    def student_subject_dashboard_vw_route():
        return student_subject_dashboard_vw()



    @app.route(LEARNING + '/student_planner_dashboard', methods=['GET'])
    def student_planner_dashboard_route():
        return get_student_planner_dashboard()



    @app.route(LEARNING + "/get_multi_chapter_tests", methods=["GET"])
    def get_multi_chapter_tests_route():
        return get_multi_chapter_tests()


    @app.route(LEARNING + "/get_student_subjects_tab_info", methods=["GET"])
    def get_student_subjects_tab_info_route():
        return get_student_subjects_tab_info()
    
    
    
    @app.route(LEARNING + "/student_dashboard_view", methods=["GET"])
    def student_dashboard_view_route():
        return get_student_dashboard_view()



    @app.route(PARENT_TEACHER_URL + "/get_study_material_v3", methods=["GET"])
    def get_study_material_v3_route():
        return sp_get_study_material_v3()