from flask import Flask
from flask_restplus import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import abort
import vk

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ACCESS_TOKEN =''
db = SQLAlchemy(app)
api = Api(app)

class Group(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	users_count = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return '<Group %r>' % self.users_count

db.create_all()

@api.route('/group/<int:group_id>/users')
class UsersCount(Resource):
	def get(self, group_id):
		res =Group.query.filter_by(id=group_id)
		if res .count():
			group =res .first()
			count =group .users_count
		else:
			try:
				session = vk.Session(access_token=ACCESS_TOKEN)
				vk_api = vk.API(session, v='5.80')
				count = vk_api.users.search(group_id=group_id)['count']
			except vk.exceptions.VkAPIError as error:
				abort(400, error)
			group = Group(id=group_id, users_count=count)
			db.session.add(group)
			db.session.commit()
		return {'count': count}

if __name__ == '__main__':
	app.run(debug=True)