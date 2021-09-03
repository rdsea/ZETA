from flask_swagger_ui import get_swaggerui_blueprint

class SwaggerBluprint():
    def get_swaggerui_blueprint(self):
        ### swagger specific ###
        SWAGGER_URL = '/swagger'
        API_URL = '/static/openapi.yaml'
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={
                'app_name': "service_point"
            }
        )
        return SWAGGERUI_BLUEPRINT, SWAGGER_URL

