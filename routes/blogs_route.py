from controllers.blogs.blog_controller import (
    get_blogs, insert_update_blog, delete_blog, get_public_blogs,
    get_seo_settings, insert_update_seo, delete_seo,
    get_categories, insert_update_category, delete_category, get_category_dropdown,
    get_authors, admin_login, admin_get_dashboard
)
from flask import send_from_directory
import os

def register_blog_routes(app):
    BLOG_URL = '/api/v1/blogs'

    # admin
    @app.route(BLOG_URL + '/admin-login', methods=['POST'])
    def login_route():
        return admin_login()

    @app.route(BLOG_URL + '/admin-dashboard', methods=['GET'])
    def admin_dashboard_route():
        return admin_get_dashboard()

    # category
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

    # blogs
    @app.route(BLOG_URL + '/blogs', methods=['GET'])
    def blog_list_route():
        return get_blogs()

    @app.route(BLOG_URL + '/blog/insert-update', methods=['POST'])
    def blog_save_route():
        return insert_update_blog()

    @app.route(BLOG_URL + '/blog/delete', methods=['POST'])
    def blog_delete_route():
        return delete_blog()

    @app.route(BLOG_URL + '/public-blogs', methods=['GET'])
    def public_blogs():
        return get_public_blogs()

    # seo
    @app.route(BLOG_URL + '/seo-settings', methods=['GET'])
    def seo_settings_route():
        return get_seo_settings()

    @app.route(BLOG_URL + '/seo/insert-update', methods=['POST'])
    def seo_save_route():
        return insert_update_seo()

    @app.route(BLOG_URL + '/seo/delete', methods=['POST'])
    def seo_delete_route():
        return delete_seo()

    # authors
    @app.route(BLOG_URL + '/authors-dropdown', methods=['GET'])
    def author_list_route():
        return get_authors()

    # uploads
    @app.route('/uploads/blogs/<filename>')
    def blog_images(filename):
        BASE_DIR = "/home/site/wwwroot"
        UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "blogs")
        return send_from_directory(UPLOAD_FOLDER, filename)