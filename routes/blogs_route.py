from controllers.blogs.get_blogs import get_blogs
from controllers.blogs.insert_update_blog import insert_update_blog
from controllers.blogs.delete_blog import delete_blog
from controllers.blogs.get_public_blogs import get_public_blogs


def register_blog_routes(app):

    BLOG_URL = '/api/v1/blogs'

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