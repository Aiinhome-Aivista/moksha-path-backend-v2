from controllers.blogs.blog_controller import get_blogs, insert_update_blog, delete_blog, get_public_blogs


def register_blog_routes(app):

    BLOG_URL = '/api/v1/blogs'

    @app.route(BLOG_URL + '/blogs', methods=['GET'])
    def get_blogs_route():
        return get_blogs()

    @app.route(BLOG_URL + '/blog/insert-update', methods=['POST'])
    def insert_update_blog_route():
        return insert_update_blog()

    @app.route(BLOG_URL + '/blog/delete', methods=['POST'])
    def delete_blog_route():
        return delete_blog()

    @app.route(BLOG_URL + '/public-blogs', methods=['GET'])
    def get_public_blogs_route():
        return get_public_blogs()