import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import get_db_connection
import sys

from controllers.common.get_academic_masters import add_institute, get_user_academic_details_nodependices
from controllers.common.get_institute_hierarchy import get_institute_hierarchy
from controllers.common.user_controller_with_paginations import get_all_usernames_with_paginations
from controllers.parents.add_parent_student_mapping import add_parent_student_mapping, create_and_map_dependent_profile, get_active_user_student_parent_list, get_invitation_all_summary, get_pending_mapping_requests, manage_parent_student_mapping, search_user_for_mapping
from controllers.parents.get_teacher_dashboard import get_teacher_dashboard_assessments
from controllers.parents.get_user_detils import get_academic_hierarchy
from controllers.parents.student_notification_assessments import get_student_notification_assessments
from controllers.parents.usp_v1_get_teacher_planner_get_dashboard import get_teacher_learning_planner_dashboard
from controllers.registration.add_profile import add_profile_v4
from controllers.registration.get_students_list_by_academics import get_students_list_by_academics
from controllers.registration.registration import   select_profile_v4, send_ui_otp_v4,verify_and_login_v4
from controllers.students.adaptive_assessment.finish_adaptive_assessment import finish_adaptive_assessment
from controllers.students.adaptive_assessment.get_next_adaptive_question import get_next_adaptive_question
from controllers.students.adaptive_assessment.create_adaptive_set import create_adaptive_set
from controllers.students.adaptive_assessment.get_student_assessments import anddaptive_get_student_assessments
from controllers.students.adaptive_assessment.retake_details import get_retake_details
from controllers.students.adaptive_assessment.save_adaptive_answer import save_adaptive_answer
from controllers.students.adaptive_assessment.start_assessment import addaptive_start_assessment
from controllers.students.adaptive_assessment.usp_get_addaptive_retake_questions import   start_adaptive_retake
from controllers.students.assessment.finish_report_assessment import get_evaluation_dashboard, process_evaluation_data
from controllers.students.assessment.new_assment_with_log.assment_save_single_answers_log import assment_save_single_answers_log
from controllers.students.assessment.new_assment_with_log.attempt_controller_with_log import finish_assessment_with_log
from controllers.students.dashboart import get_main_dashboard
from controllers.students.usp_v1_get_student_assessments import get_student_assessments_chapters_details
from controllers.study_meterial.get_study_meterial import get_study_material
from controllers.study_meterial.upload_study_meterial import upload_study_material, UPLOAD_FOLDER as NOTES_UPLOAD_FOLDER
from controllers.study_meterial.get_study_meterial_v3 import sp_get_study_material_v3
from controllers.study_meterial.get_teacher_study_meterial import get_teacher_study_material
sys.dont_write_bytecode = True


# Import Controllers
from controllers.common.forgot_user.forgot_username_email import   get_user_details, recover_username_send_otp, recover_username_verify
from controllers.common.get_save_academic_details.get_rolesname import get_all_roles
from controllers.common.get_save_academic_details.get_subject_by_criteria import get_subjects_by_criteria
from controllers.common.get_save_academic_details.get_user_academic_details import get_user_academic_details
from controllers.common.login.login_otp_verified import login_login_user, login_send_ui_otp, login_verify_ui_otp
from controllers.common.login.logout import login_logout_user
from controllers.common.registration_and_login_otp_verified import (
    check_username_availability,
    complete_ui_signup,
    get_username_suggestions,
    send_ui_otp,
    verify_ui_otp
)
from controllers.common.page_menu_acess import get_user_menu
from controllers.common.registration import register_user
from controllers.common.academic import get_academic_masters
from controllers.common.get_save_academic_details.save_academic_details import save_academic_details
from controllers.common.subscription.validate_controller import validate_subscription
from controllers.parents.add_child_student import add_child_student
from controllers.common.subscription_pricing_controller import get_subscription_plans_post
from controllers.common.validate_subscription_amount import validate_subscription_amount
from controllers.common.decode_access_token import decode_access_token
from controllers.common.user_profile import get_user_profiles, switch_profile
from controllers.common.get_save_academic_details.save_user_academic_details import  save_user_academic_details
from controllers.students.assessment.ai_question_controller import generate_and_store_questions 
from controllers.students.assessment.assign_controller import assign_auto_assessment
from controllers.students.assessment.attempt_controller import finish_assessment, get_assessment_details, save_single_answer, start_assessment_attempt, submit_assessment_result
from controllers.students.assessment.student_dashboard_controller import get_student_assessments
from controllers.students.assessment.teacher_assign_class_controller import teacher_assign_class_assessment
from controllers.students.assessment.teacher_assign_controller import teacher_assign_assessment
from controllers.students.generate_plan_controller import generate_auto_plan
from controllers.students.get_dashboard_controller import get_student_dashboard
from controllers.students.get_planner_controller import get_learning_planner
from controllers.students.update_preferences_controller import update_study_hours
from controllers.students.update_priority_controller import update_priority
from controllers.students.update_topic_status_controller import update_topic_status
from controllers.common.profile_image.profile_image_controller import get_profile_image, upload_profile_image
from controllers.students.assessment.retake_assessment_controller import retake_assessment
from controllers.common.get_save_academic_details.save_subscription_draft import save_subscription_draft
from controllers.common.complete_subscription import complete_subscription
from controllers.common.get_save_academic_details.get_or_generate_chapter_topic_resources import get_or_generate_chapter_topic_resources
from controllers.common.subscription.subscription_invite_controller import (send_invite_by_id, get_my_invites, respond_invite_username, get_invite_history, undo_invite
)
from controllers.common.user_controller import get_all_usernames
from controllers.common.subscription.manage_subscription_controller import get_full_manage_subscription_page

from controllers.students.student_dashboard_kpi import (get_subject_confidence, get_progressing_ability, get_consistency_score, get_exam_readiness, get_pending_tasks, get_subjectwise_average_score, get_student_subjects, get_student_strength_weakness )

from controllers.teachers.teacher_dashboard_controller import (get_bucket_performance, get_teacher_subjects, get_subject_performance, get_chapter_performance, get_class_exam_performance, get_curriculum_coverage, get_upcoming_chapters, get_pending_topics, get_teacher_profile_details, get_teacher_top_bottom_students
)

from controllers.registration.get_users_by_token_contact import get_users_by_token_contact
from controllers.common.subscription.get_user_subscriptions_list import get_user_subscriptions_list
from controllers.parents.parent_dashboard_controller import (
    get_parent_children_dropdown, get_parent_subject_confidence, get_parent_progressing_ability, 
    get_parent_consistency_score, get_parent_exam_readiness, get_parent_pending_tasks, 
    get_parent_subjectwise_average_score, get_parent_student_subjects, get_parent_student_strength_weakness
)
from controllers.parents.get_parent_profile_details import get_parent_profile_details
# Blogs Controllers
from controllers.blogs.admin_login_controller import admin_login
from controllers.blogs.category_controller import get_categories, insert_update_category, delete_category, get_category_dropdown
from controllers.blogs.blog_controller import get_blogs, insert_update_blog, delete_blog, get_public_blogs, UPLOAD_FOLDER
from controllers.blogs.seo_controller import get_seo_settings, insert_update_seo, delete_seo
from controllers.blogs.dashboard_controller import admin_get_dashboard

from controllers.common.user_profile_details import get_user_profile, update_user_profile, get_academic_details

from controllers.institute_admin.teacher_assign_controller import assign_teacher, remove_teacher, get_assigned_teachers, get_available_teachers
from controllers.blogs.author_controller import get_authors
from controllers.institute_admin.bulk_teacher_upload_controller import bulk_upload_teachers
from newcontroller.upsert_teacher_chapter_planner import  upsert_teacher_chapter_planner,get_institute_admin_summary,get_teacher_planer_data, get_student_planner_dashboard
from controllers.institute_admin.bulk_teacher_upload_controller_v2 import bulk_upload_users_controller_v2


from newcontroller.upsert_teacher_chapter_planner import  upsert_teacher_chapter_planner,get_institute_admin_summary,get_teacher_planer_data, generate_test_from_planner, get_student_subjects_tab_info
# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 2. URL CONSTANTS (Configuration)
# ==========================================
# You can easily change versions here (e.g., '/api/v1/auth')
AUTH_URL = '/api/v1/auth'
ACADEMIC_URL = '/api/v1/academic'
USER_URL = '/api/v1/user'
PARENT_TEACHER_URL = '/api/v1/parent_teacher'
AUTH_LOGIN_URL = '/api/v1/auth/login'
SUBCRIPTION_URL = '/api/v1/subscription'
LEARNING = '/api/v1/learning'
ROOT_URL = ''  # For endpoints currently at the root level
BLOG_URL = '/api/v1/blogs'
# ANALYTICS_URL = "/api/v1/log"
ANALYTICS_URL = "/api/v1/analytics"
INSTITUTE_ADMIN_URL = '/api/v1/institute_admin'

# ==========================================
# 3. ROUTES
# ==========================================
@app.route("/")
def health():
    return "API is running"

# --- COMMON ROUTES ---
# @app.route(ROOT_URL + '/register', methods=['POST'])
# def register_route():
#     return register_user()


@app.route(SUBCRIPTION_URL + '/validate', methods=['POST'])
def validate_subscription_route():
    return validate_subscription()


@app.route(SUBCRIPTION_URL + '/plans', methods=['POST'])
def subscription_plans_route():
    return get_subscription_plans_post()


@app.route(SUBCRIPTION_URL + '/validate_plan_amount', methods=['POST'])
def validate_subscription_amount_route():
    return validate_subscription_amount()


@app.route(SUBCRIPTION_URL + '/save_subscription_draft', methods=['POST'])
def save_draft():
    return save_subscription_draft()

@app.route(SUBCRIPTION_URL + '/complete_subscription', methods=['POST'])
def complete_subscription_route():      
    return complete_subscription()

# --- NEW INVITE ROUTES ---
@app.route(SUBCRIPTION_URL + '/invite_send', methods=['POST'])
def send_invite_route():
    return send_invite_by_id()

@app.route(SUBCRIPTION_URL + '/invite_list', methods=['GET'])
def list_invite_route():
    return get_my_invites()

@app.route(SUBCRIPTION_URL + '/invite_respond', methods=['POST'])
def respond_invite_route():
    return respond_invite_username()

@app.route(SUBCRIPTION_URL + '/subscription_list', methods=['GET'])
def get_full_manage_subscription_route():
    return get_full_manage_subscription_page()

@app.route(SUBCRIPTION_URL + '/invite_history', methods=['GET'])
def invite_history_route():
    return get_invite_history()

@app.route(SUBCRIPTION_URL + '/undo_invite', methods=['POST'])
def undo_invite_route():
    return undo_invite()

@app.route(SUBCRIPTION_URL + '/user_subscriptions', methods=['GET'])
def get_user_subscriptions_route():
    return get_user_subscriptions_list()

# ==== --- Base Url===
@app.route(USER_URL + '/profile_image/upload', methods=['POST'])
def route_upload_profile_image():
    return upload_profile_image()

@app.route(USER_URL + '/profile_image', methods=['GET'])
def route_get_profile_image():
    return get_profile_image()


@app.route(USER_URL + '/menu/page_acess', methods=["POST"])  # Changed from GET to POST
def get_user_menu_route():
    return get_user_menu()

@app.route(USER_URL +'/profile_info', methods=['GET'])
def fetch_profile():
    return get_user_profile()

@app.route(USER_URL +'/update_profile', methods=['POST'])
def save_profile():
    return update_user_profile()

@app.route(USER_URL +'/user_academic_info', methods=['GET'])
def user_academic_details():
    return get_academic_details()
@app.route(USER_URL + '/add_parent_student_mapping', methods=["POST"])  # Changed from GET to POST
def add_parent_student_mapping_route():
    return add_parent_student_mapping()

@app.route(USER_URL + '/search_user_for_mapping', methods=["GET"])  # Changed from GET to POST
def search_user_for_mapping_route():
    return search_user_for_mapping()

@app.route(USER_URL + '/create_and_map_dependent_profile', methods=["POST"])
def create_and_map_dependent_profile_route():
    return create_and_map_dependent_profile()

@app.route(USER_URL + '/get_active_user_student_parent_list', methods=["GET"])
def get_active_user_student_parent_list_route():
    return get_active_user_student_parent_list()


# --- ACADEMIC ROUTES ---
@app.route(ACADEMIC_URL + '/get_user_academic_details_nodependices', methods=["GET"])
def get_user_academic_details_nodependices_route():
    return get_user_academic_details_nodependices()

@app.route(ACADEMIC_URL + '/institute/add', methods=["POST"])
def add_institute_route():
    return add_institute()

# --- ACADEMIC ROUTES ---
@app.route(ACADEMIC_URL + '/masters', methods=["GET"])
def academic_masters_route():
    return get_academic_masters()

@app.route(ACADEMIC_URL + '/save', methods=["POST"])
def save_academic_details_route():
    return save_academic_details()

@app.route(ACADEMIC_URL + '/get_subjects_by_boards', methods=["POST"])
def get_subjects_by_criteria_route():
    return get_subjects_by_criteria()


@app.route(ACADEMIC_URL + '/save_user_academic_details', methods=["POST"])
def save_user_academic_details_route():  
    return save_user_academic_details()

@app.route(ACADEMIC_URL + '/get_user_academic_details', methods=["GET"])
def get_user_academic_details_route():
    return get_user_academic_details()
# --- AUTH ROUTES ---


@app.route(AUTH_LOGIN_URL + '/send_otp', methods=["POST"])
def login_send_otp_route():
    return login_send_ui_otp()

@app.route(AUTH_LOGIN_URL + '/verify_otp', methods=["POST"])
def login_verify_otp_route():
    return login_verify_ui_otp()

@app.route(AUTH_LOGIN_URL + '/login_session', methods=["POST"])
def login_logn_route():
    return login_login_user()

@app.route(AUTH_LOGIN_URL + '/logout', methods=["POST"])
def login_logout_user_route():
    return login_logout_user()


@app.route(AUTH_URL + '/roles', methods=["GET"])
def get_roles_route():
    return get_all_roles()

@app.route(AUTH_URL + '/send_otp', methods=["POST"])
def send_ui_otp_route():
    return send_ui_otp()

@app.route(AUTH_URL + '/verify_otp', methods=["POST"])
def verify_ui_otp_route():
    return verify_ui_otp()

@app.route(AUTH_URL + '/register', methods=["POST"])
def complete_ui_signup_route():
    return complete_ui_signup()

# SCENARIO 1: Forgot Username (OTP Flow)
@app.route(AUTH_URL + '/recovery/send_otp', methods=["POST"])
def recover_send_otp_route():
    return recover_username_send_otp()

@app.route(AUTH_URL + '/recovery/verify_otp', methods=["POST"])
def recover_verify_otp_route():
    return recover_username_verify()

# SCENARIO 2: Find Details by Username (No OTP)
@app.route(AUTH_URL + '/find_details', methods=["POST"])
def find_details_route():
    return get_user_details()


@app.route(AUTH_URL + '/decode_token', methods=["POST"])
def decode_access_token_route():
    return decode_access_token()

@app.route(AUTH_URL +'/user_profiles', methods=["GET"])
def get_profiles_route():
    return get_user_profiles()

@app.route(AUTH_URL +'/switch_profile', methods=["POST"])
def switch_profile_route():
    return switch_profile()

# --- USER/PARENT ROUTES ---
@app.route(PARENT_TEACHER_URL + '/add_child', methods=["POST"])
def add_child_student_route():
    return add_child_student()


# --- USERNAME UTILITY ROUTES ---
# These are currently at the root level in your example
@app.route(USER_URL + '/username_suggestions', methods=["GET"])
def username_suggestions_route():
    return get_username_suggestions()

@app.route(USER_URL + '/username_check', methods=["POST"])
def username_check_route():
    return check_username_availability()

@app.route(USER_URL + '/username_list', methods=['GET'])
def get_usernames_route():
    return get_all_usernames()

@app.route(USER_URL + '/get_institute_hierarchy', methods=['GET'])
def get_institute_hierarchy_route():
    return get_institute_hierarchy()

@app.route(USER_URL + '/get_all_usernames_with_paginations', methods=['POST'])
def get_all_usernames_with_paginations_route():
    return get_all_usernames_with_paginations()

@app.route(USER_URL + '/manage_parent_student_mapping', methods=['POST'])
def manage_parent_student_mapping_route():
    return manage_parent_student_mapping()

@app.route(USER_URL + '/get_pending_mapping_requests', methods=['GET'])
def get_pending_mapping_requests_route():
    return get_pending_mapping_requests()

@app.route(USER_URL + '/get_invitation_all_summary', methods=['GET'])
def get_invitation_all_summary_route():
    return get_invitation_all_summary()


# ==========================================
# learning_routes

# ==========================================
# @app.route(LEARNING + '/planner', methods=["POST"])
# def get_learning_planner_route():
#     return get_learning_planner()

@app.route(LEARNING + '/generate_auto_plan', methods=["POST"])
def generate_auto_plan_route():
    return generate_auto_plan()

@app.route(LEARNING + '/student/update_study_hours', methods=["POST"])
def update_study_hours_route():
    return update_study_hours()


@app.route(LEARNING + '/student/get_main_dashboard', methods=["GET"])
def get_main_dashboard_route():
    return get_main_dashboard()

@app.route(LEARNING + '/student/learning_planner', methods=["GET"])
def get_learning_planner_route_test():
    return get_learning_planner()  

@app.route(LEARNING + '/teacher/learning_planner', methods=["GET"])
def get_teacher_learning_planner_dashboard_route():
    return get_teacher_learning_planner_dashboard()  

@app.route(LEARNING + '/student/update_topic_status', methods=["POST"])
def update_topic_status_route():
    return update_topic_status()  

@app.route(LEARNING + '/student/update_priority', methods=["POST"])
def update_priority_route():
    return update_priority() 

@app.route(LEARNING + '/student/get_student_dashboard', methods=["GET"])
def get_student_dashboard_route():
    return get_student_dashboard() 

@app.route(LEARNING + '/get_or_generate_chapter_topic_resources', methods=["POST"])
def get_chapter_topic_ai_resources_route():
    return get_or_generate_chapter_topic_resources()

# ==========================================
# Student Assessment Routes
# ==========================================
@app.route(LEARNING + '/store_questions', methods=["POST"])
def generate_and_store_questions_route():
    return generate_and_store_questions()

@app.route(LEARNING + '/assign_assessment', methods=["POST"])
def assign_assessment_route():
    return assign_auto_assessment()

@app.route(LEARNING + '/student/assessments', methods=["GET"])
def get_student_assessments_route():
    return get_student_assessments()

@app.route(LEARNING + '/student/get_student_assessments_chapters_details', methods=["GET"])
def get_student_assessments_chapters_details_route():
    return get_student_assessments_chapters_details()


@app.route(LEARNING + '/assessment/details', methods=["GET"])
def get_assessment_details_route():
    return get_assessment_details()

@app.route(LEARNING + '/assessment/start', methods=["POST"])
def start_assessment_route():
    return start_assessment_attempt()

@app.route(LEARNING + '/assessment/submit', methods=["POST"])
def submit_assessment_route():
    return submit_assessment_result() 

@app.route(LEARNING + '/assessment/save_answer', methods=["POST"])
def save_single_answer_route():
    return save_single_answer()
# New log lojic Save answers for assments
@app.route(LEARNING + '/assessment/save_answer_with_log', methods=["POST"])
def assment_save_single_answers_log_route():
    return assment_save_single_answers_log()

@app.route(LEARNING + '/assessment/finish', methods=["POST"])
def finish_assessment_route():
    return finish_assessment()
# finish_with_log
@app.route(LEARNING + '/assessment/finish_with_log', methods=["POST"])
def finish_assessment_with_log_route():
    return finish_assessment_with_log()

@app.route(LEARNING + '/teacher/assign_assessment', methods=["POST"])
def teacher_assign_assessment_route():
    return teacher_assign_assessment()

@app.route(LEARNING + '/teacher/assign_class_assessment', methods=["POST"])
def teacher_assign_class_assessment_route():
    return teacher_assign_class_assessment()

@app.route(LEARNING + '/assessment/retake', methods=["POST"])
def retake_assessment_route():
    return retake_assessment()


@app.route(LEARNING + '/get_students_list_by_academics', methods=["GET"])
def get_students_list_by_academics_route():
    return get_students_list_by_academics()

#  Addaptive quction test
@app.route(LEARNING + '/assessment/create_adaptive_set', methods=["POST"])
def create_adaptive_set_route():
    return create_adaptive_set()

@app.route(LEARNING + '/assessment/student_assessments', methods=["GET"])
def anddaptive_get_student_assessments_route():
    return anddaptive_get_student_assessments()

@app.route(LEARNING + '/assessment/addaptive_start', methods=["POST"])
def addaptive_start_assessment_route():
    return addaptive_start_assessment()

@app.route(LEARNING + '/assessment/get_next_question', methods=["GET"])
def get_next_adaptive_question_route():
    return get_next_adaptive_question()

@app.route(LEARNING + '/assessment/save_adaptive_answer', methods=["POST"])
def save_adaptive_answer_route():
    return save_adaptive_answer()

@app.route(LEARNING + '/assessment/finish_adaptive', methods=["POST"])
def finish_adaptive_assessment_route():
    return finish_adaptive_assessment()

@app.route(LEARNING + '/assessment/retake_details', methods=["POST"])
def get_retake_details_route():
    return get_retake_details()

@app.route(LEARNING + '/assessment/start_adaptive_retake', methods=["POST"])
def start_adaptive_retake_route():
    return start_adaptive_retake()


# 1. Trigger Data Processing (Batch Job)
@app.route(LEARNING + '/evaluation/process', methods=["POST"])
def process_evaluation_route():
    return process_evaluation_data()

# 2. Fetch Dashboard
@app.route(LEARNING + '/evaluation/dashboard', methods=["GET"])
def get_evaluation_dashboard_route():
    return get_evaluation_dashboard()

# ==========================================
# ANALYTICS ROUTES
# ==========================================

# Subject Confidence Slider
@app.route(LEARNING + '/analytics/confidence', methods=['GET'])
def subject_confidence_route():
    return get_subject_confidence()

# Progressing Ability
@app.route(LEARNING + '/analytics/progressing-ability', methods=['GET'])
def progressing_ability_route():
    return get_progressing_ability()

# Consistency Score
@app.route(LEARNING + '/analytics/consistency', methods=['GET'])
def consistency_score_route():
    return get_consistency_score()

# Exam Readiness
@app.route(LEARNING + '/analytics/exam-readiness', methods=['GET'])
def exam_readiness_route():
    return get_exam_readiness()

@app.route(LEARNING + '/analytics/pending-tasks', methods=['GET'])
def pending_tasks_route():
    return get_pending_tasks()

@app.route(LEARNING + '/analytics/subject-average-score', methods=['GET'])
def subject_average_score_route():
    return get_subjectwise_average_score()

@app.route(LEARNING + '/analytics/student-subjects', methods=['GET'])
def get_student_subjects_list():
    return get_student_subjects()

@app.route(LEARNING + '/analytics/strength-weakness', methods=['GET'])
def student_strength_weakness_route():
    return get_student_strength_weakness()

@app.route(LEARNING + '/student_planner_dashboard', methods=['GET'])
def student_planner_dashboard_route():
    return get_student_planner_dashboard()

@app.route(LEARNING + '/generate_test_from_planner', methods=['POST'])
def generate_test_from_planner_route(): 
    return generate_test_from_planner()


#Newly added routes can be placed here following the same pattern.#
# Newly added routes can be placed here following the same pattern.#
@app.route(AUTH_URL + '/get_academic_hierarchy', methods=["GET"])
def get_academic_hierarchy_route():
    return get_academic_hierarchy()

@app.route(AUTH_URL + '/get_teacher_student_status_dashboard', methods=["GET"])
def get_teacher_dashboard_assessments_route():
    return get_teacher_dashboard_assessments()

@app.route(AUTH_URL + '/student/notification_assessments', methods=["GET"])
def get_student_notification_assessments_route():
    return get_student_notification_assessments()


@app.route(AUTH_URL + '/send_ui_otp_v4', methods=["POST"])
def send_ui_otp_v4_route():
    return send_ui_otp_v4()


@app.route(AUTH_URL + '/verify_account', methods=["POST"])
def verify_account_get_profiles_route():
    return verify_and_login_v4()

@app.route(AUTH_URL + '/select_profile', methods=["POST"])
def select_profile_route():
    return select_profile_v4()


@app.route(AUTH_URL + '/add_profile', methods=["POST"])
def add_profile_route():
    return add_profile_v4()

@app.route(AUTH_URL + '/get_users_by_token_contact', methods=["GET"])
def get_users_by_token_contact_route():
    return get_users_by_token_contact()


# Teacher Dashboard Routes
@app.route(PARENT_TEACHER_URL + '/dashboard/bucket-performance', methods=['GET'])
def teacher_bucket_perf_route():
    return get_bucket_performance()

@app.route(PARENT_TEACHER_URL + '/dashboard/subjects', methods=['GET'])
def teacher_subjects_route():
    return get_teacher_subjects()

@app.route(PARENT_TEACHER_URL + '/dashboard/subject-performance', methods=['GET'])
def teacher_subject_perf_route():
    return get_subject_performance()

@app.route(PARENT_TEACHER_URL + '/dashboard/chapter-performance', methods=['GET'])
def teacher_chapter_perf_route():
    return get_chapter_performance()

@app.route(PARENT_TEACHER_URL + '/dashboard/class-exam-performance', methods=['GET'])
def teacher_class_exam_perf_route():
    return get_class_exam_performance()

@app.route(PARENT_TEACHER_URL + '/dashboard/curriculum-coverage', methods=['GET'])
def teacher_curriculum_coverage_route():
    return get_curriculum_coverage()

@app.route(PARENT_TEACHER_URL + '/dashboard/upcoming-chapters', methods=['GET'])
def teacher_upcoming_chapters_route():
    return get_upcoming_chapters()

@app.route(PARENT_TEACHER_URL + '/dashboard/pending-topics', methods=['GET'])
def teacher_pending_topics_route():
    return get_pending_topics()

@app.route(PARENT_TEACHER_URL + '/dashboard/teacher-profile', methods=['GET'])
def teacher_profile_route():
    return get_teacher_profile_details()

@app.route(PARENT_TEACHER_URL + '/dashboard/top-bottom-students', methods=['GET'])
def teacher_top_bottom_students_route():
    return get_teacher_top_bottom_students()
# ==========================================
# Parent Dashboard Routes
# ==========================================
# 1. Dropdown API (No query params needed)
@app.route(PARENT_TEACHER_URL + '/dashboard/parent/children', methods=['GET'])
def parent_children_route():
    return get_parent_children_dropdown()

# 2. KPI APIs (Must pass ?student_id=X in UI)
@app.route(PARENT_TEACHER_URL + '/dashboard/parent/confidence', methods=['GET'])
def parent_confidence_route():
    return get_parent_subject_confidence()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/progressing-ability', methods=['GET'])
def parent_progressing_route():
    return get_parent_progressing_ability()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/consistency', methods=['GET'])
def parent_consistency_route():
    return get_parent_consistency_score()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/exam-readiness', methods=['GET'])
def parent_readiness_route():
    return get_parent_exam_readiness()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/pending-tasks', methods=['GET'])
def parent_pending_route():
    return get_parent_pending_tasks()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/subject-average-score', methods=['GET'])
def parent_average_score_route():
    return get_parent_subjectwise_average_score()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/strength-weekness', methods=['GET'])
def get_parent_student_strength_weakness_route():
    return get_parent_student_strength_weakness()

@app.route(PARENT_TEACHER_URL + '/dashboard/parent/parent-profile', methods=['GET'])
def parent_profile_route():
    return get_parent_profile_details()

@app.route(PARENT_TEACHER_URL + '/teacher_chapter_planner_upsert', methods=['POST'])
def upsert_teacher_chapter_planner_route(): 
    return upsert_teacher_chapter_planner()

@app.route(PARENT_TEACHER_URL + '/institute_admin_summary', methods=['GET'])
def get_institute_admin_summary_route():        
    return get_institute_admin_summary()

@app.route(PARENT_TEACHER_URL + '/teacher_planner_data', methods=['GET'])
def get_teacher_planer_data_route():
    return get_teacher_planer_data()


# Blogs Routes
@app.route(BLOG_URL + '/admin-login', methods=['POST'])
def login_route():
    return admin_login()

@app.route(BLOG_URL + '/categories', methods=['GET'])
def category_list_route():
    return get_categories()


@app.route(BLOG_URL + '/category/insert-update', methods=['POST'])
def category_save_route():
    return insert_update_category()


@app.route(BLOG_URL + '/category/delete', methods=['POST'])
def category_delete_route():
    return delete_category()

@app.route(BLOG_URL + '/category-dropdown', methods=['GET'])
def category_dropdown_route():
    return get_category_dropdown()

@app.route(BLOG_URL + '/blogs', methods=['GET'])
def blog_list_route():
    return get_blogs()


@app.route(BLOG_URL + '/blog/insert-update', methods=['POST'])
def blog_save_route():
    return insert_update_blog()


@app.route(BLOG_URL + '/blog/delete', methods=['POST'])
def blog_delete_route():
    return delete_blog()

@app.route(BLOG_URL + '/seo-settings', methods=['GET'])
def seo_settings_route():
    return get_seo_settings()

@app.route(BLOG_URL + '/seo/insert-update', methods=['POST'])
def seo_save_route():
    return insert_update_seo()

@app.route(BLOG_URL + '/seo/delete', methods=['POST'])
def seo_delete_route():     
    return delete_seo() 

@app.route(BLOG_URL + '/admin-dashboard', methods=['GET'])
def admin_dashboard_route():
    return admin_get_dashboard()

@app.route(BLOG_URL + '/public-blogs',methods=['GET'])
def public_blogs():
    return get_public_blogs()

@app.route(BLOG_URL + '/authors-dropdown', methods=['GET'])
def author_list_route():
    return get_authors()

@app.route('/uploads/blogs/<filename>')
def blog_images(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# Analytics Url
@app.route(ANALYTICS_URL + "/user-events", methods=["POST"])
def log_user_activity_route():
    return log_user_activity()


# Analytics Routes
@app.route(ANALYTICS_URL + "/log_activity", methods=["POST"])
def log_activity_route():
    return log_activity()


# 'uploads/blogs'

# ==========================================
# Institute Admin Routes
# ==========================================
@app.route(INSTITUTE_ADMIN_URL + '/assign_teacher', methods=["POST"])
def institute_assign_teacher_route():
    return assign_teacher()

@app.route(INSTITUTE_ADMIN_URL + '/remove_teacher', methods=["POST"])
def institute_remove_teacher_route():
    return remove_teacher()

@app.route(INSTITUTE_ADMIN_URL + '/assigned_teacher_list', methods=["GET"])
def institute_get_teachers_route():
    return get_assigned_teachers()

@app.route(INSTITUTE_ADMIN_URL + '/available_teachers', methods=["GET"])
def institute_get_available_teachers_route():
    return get_available_teachers()


@app.route(PARENT_TEACHER_URL + "/upload_study_material", methods=["POST"])
def upload_study_material_route():
    return upload_study_material()

@app.route(PARENT_TEACHER_URL + "/get_teacher_study_material", methods=["GET"])
def get_teacher_study_material_route():
    return get_teacher_study_material()

@app.route('/uploads/notes/<path:filename>')
def serve_notes(filename):
    return send_from_directory(NOTES_UPLOAD_FOLDER, filename)

@app.route(PARENT_TEACHER_URL + "/get_study_material", methods=["GET"])
def get_study_material_route():
    return get_study_material()

@app.route(PARENT_TEACHER_URL + "/get_study_material_v3", methods=["GET"])
def get_study_material_v3_route():
    return sp_get_study_material_v3()

# @app.route(INSTITUTE_ADMIN_URL + '/upload_teacher_list', methods=["POST"])
# def bulk_upload_teachers_route():
#     return bulk_upload_teachers()


@app.route(INSTITUTE_ADMIN_URL + "/bulk_upload_users", methods=["POST"])
def bulk_upload_teachers_route():
    return bulk_upload_users_controller_v2()



@app.route(LEARNING + "/get_student_subjects_tab_info", methods=["GET"])
def get_student_subjects_tab_info_route():
    return get_student_subjects_tab_info()


# ==========================================
# 4. UTILITIES & STARTUP
# ==========================================
def check_db_connection():
    conn = None
    try:
        conn = get_db_connection()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f" Database connection failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db_connection()    
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"    
    print(f"Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
