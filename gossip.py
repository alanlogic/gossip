import random

from flask import (Flask, request, redirect, url_for, abort,
                   render_template, session, flash, jsonify)

from database import db_session
from form import LoginForm, RegisterForm
from model import Gossip, Friend, User, Player, Invite

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'myGossip'


def user_exist(user_id):
    user = User.query.filter_by(user_id=user_id)
    if user is None:
        abort(404)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def main_index():
    return render_template('index.html')


@app.route('/<int:user_id>')
def user_index(user_id):
    user_exist(user_id)
    return render_template('user_page.html')


@app.route('/my-gossip')
def my_gossip():
    page = request.args.get('page', 0)
    gossips = (db_session.query(Gossip).
               filter(Gossip.user_id == session['user_id']).
               offset(page * 10).limit(10).all())
    return jsonify(gossips)


@app.route('/infoceter')
def infocenter():
    page = request.args.get('page', 0)
    friends = Friend.query.filter(Friend.user1 == session['user_id']).all()
    friends_id = map(lambda friend: friend.user_id, friends)
    r_gossips = (Gossip.query.join(Player, Gossip.user_id == Player.user_id).
                 filter(Gossip.user_id.in_(friends_id)).
                 offset(page * 10).limit(10).all())
    return jsonify(r_gossips)


@app.route('/rank')
def rank():
    page = request.args.get('page', 0)
    friends = Friend.query.filter(Friend.user1 == session['user_id']).all()
    friends_id = map(lambda friend: friend.user_id, friends)
    if request.args.get('type') == 'week':
        ranked = (Player.query.filter(Player.user_id.in_(friends_id)).
                  order_by(Player.gold).offset(page * 10).limit(10).all())
    else:
        ranked = (Player.query.filter(Player.user_id.in_(friends_id)).
                  order_by(Player.diamond).offset(page * 10).limit(10).all())
    return jsonify(ranked)


@app.route('/fish')
def fish():
    # 50% probability get a gossip
    # question: how to solve the problem of user maybe delete the gossip
    success = random.randint(0, 1)
    if success:
        pass


# problem: only user look up the messagebox,otherwise won't get the Invite
@app.route('/message-box')
def message_box():
    messages = Invite.query.filter(Invite.user2 == session['user_id']).all()
    return jsonify(messages)


@app.route('/agree')
def agree():
    # todo:add auth about the user_id
    inviter_id = request.args.get('inviter', None)
    if inviter_id is not None:
        db_session.add(Friend(session['user_id'], inviter_id))


@app.route('/add-gossip', methods=['Post'])
def add_gossip():
    db_session.add(Gossip(request.form))
    db_session.commit()
    return jsonify('ok')


@app.route('/add-friend')
def add_friend():
    username = request.args.get('username', None)
    if username is not None:
        user_id = User.query.filter(User.username == username).first()
        if user_id is not None:
            db_session.add(Invite(user1=session['user_id'], user2=user_id))
            db_session.add(Invite(user1=user_id, user2=session['user_id']))
            db_session.commit()
    return jsonify('ok')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = form.get_user().user_id
        session['user_id'] = user_id
        return redirect(url_for('user_index', user_id=user_id))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('main_index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.add_user()  # There has a problem
        return redirect(url_for(user.user_id))
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run()
