from flask import Flask, request
from flask_restful import Api, Resource
from models import db, Object

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_structure.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db.init_app(app)

error_500 = {'error': 'Ошибка обращения к БД'}, 500


@app.before_first_request
def create_db():
    """Создается БД, таблицы, если их нет"""
    db.create_all()


# def check_db_request(req):
#     """Функция проверки обращения к БД, возвращает ошибку 500 и описание"""
#     try:
#         result = req
#         print(req, result)
#         return result
#     except:
#         return error_500


def get_descendant_tree(get_object):
    """Получение древовидного отображения потомков объекта"""
    # print(f'Run get_descendant_tree(get_object) \n{get_object}')
    descendant = []
    if get_object.type != 'folder':  # Проверяем, если объект не папка, возвращаем объект
        print(f'Объект не папка, возвращаем объект')
        return get_object.json()

    try:
        get_object_descendant = Object.query.filter(Object.parent_id == get_object.id).all()  # Получаем объекты
        # наследники
    except:
        return error_500

    if not get_object_descendant:
        return get_object.json()

    for i in get_object_descendant:
        descendant.append(get_descendant_tree(i))
        result = get_object.json()
        result['descendant'] = descendant

    return result


class AllObjectsView(Resource):
    """Получение всех объектов из БД, с учетом GET параметра '?filter=name'"""

    def get(self):
        get_param = request.args.get('filter')
        if get_param:
            try:
                all_objects = Object.query.filter(Object.name.like(f'%{get_param}%'))
            except:
                return error_500
            if not all_objects[:]:
                return {'error': 'Объектов, удовлетворяющих фильтру, не существует'}, 404
        else:
            try:
                all_objects = Object.query.all()
            except:
                return error_500
        return [i.json() for i in all_objects]


class OneObjectView(Resource):
    """Получение одного объекта из БД"""

    def get(self, pk):
        try:
            one_object = Object.query.get(pk)
        except:
            return error_500
        if not one_object:
            return {'error': 'Объект не существует'}, 404

        return get_descendant_tree(one_object)
        # return one_object.json()


api.add_resource(AllObjectsView, '/api/v1/object/', '/api/v1/object/0')
api.add_resource(OneObjectView, '/api/v1/object/<int:pk>')


@app.route('/api/v1/object/<string:pk>')
def get_id_str(pk):
    """Вызываем ошибку, если id объекта задан не цифрой"""
    return {'error': f'id задан не цифрой: /{pk}'}, 400


if __name__ == '__main__':
    app.run(debug=True)
