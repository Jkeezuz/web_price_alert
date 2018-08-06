from flask import  blueprints, Blueprint


item_blueprint = Blueprint('items', __name__)


@item_blueprint.route('/item/<string:name>')
def item_page():
    pass
