from flask import render_template, url_for, flash, redirect, request, abort
from SCApp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from SCApp.models import User, Post
from SCApp import app, db, bcrypt, mail
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from PIL import Image
import secrets
import os


@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page', 1, type=int) # Getting the first page as a default
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=1)
	return render_template('home.html', posts=posts)

@app.route("/about")
def about():
	return "about page"

@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #decode part just turns the hashed pw bytes into a string
		user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
		db.session.add(user)
		db.session.commit()

		#Flashes a message to let us know the post request was successful
		flash('Your account has been created!', category='success')
		return redirect(url_for('login'))

	return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			
			login_user(user, remember=form.remember_me.data)
			return redirect(url_for('home'))
			# next_page = request.args.get('next')
			
			# if next_page:	# Handles transporting the user to the intended page after they have logged in, because it was a login required page
			# 	if not is_safe_url(next_page):				
			# 		return flask.abort(400)
			# 	else:
			# 		return redirect(next_page)
			# else:
			# 	return redirect(url_for('home'))
		else:
			flash('Login unsuccessful, please try again', category='danger')

	return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_extension = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + f_extension
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
	
	#resizing the image with pillow
	output_size = 125, 125
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)

	return picture_filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.username.data
		db.session.commit()
		flash("Your account has been updated.", category="success")
		return redirect(url_for("account"))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template("account.html", title="Account", image_file=image_file, form=form)



@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()

		flash("Post Created!", category="success") # the category is a bootstrap class
		return redirect(url_for('home'))

	return render_template("create_post.html", title="New Post", form=form, legend="New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
	# querying for the post by the post id passed into the function and the route
	post = Post.query.get_or_404(post_id) 


	return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	# same story as the "post" function above, querying based on the post_id passed into the function
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403) # 403 is http response for a forbidden route
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data

		# Note: we don't need to add the data to the session because the post already exists in the database, we are just updating it
		db.session.commit()
		flash("Post has been updated", category="success")
		return redirect(url_for('post', post_id=post.id))

	elif request.method == 'GET':
		# pre filling the fields with the existing data when the request is only a get request, which would mean the user is viewing the page
		# and hasn't POSTED their updates yet
		form.title.data = post.title
		form.content.data = post.content
	return render_template("create_post.html", title="Update Post", form=form, legend="Update Post")


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	# same story as the "post" function above, querying based on the post_id passed into the function
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403) # 403 is http response for a forbidden route
	db.session.delete(post)
	db.session.commit()
	flash("Post has been deleted", category="success")
	return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type=int) # Getting the first page as a default
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=1)
	return render_template('user_posts.html', user=user, posts=posts)



def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

	msg.body = f""" To reset your password, visit the following link:
	{url_for('reset_token', token=token, _external=True)}

	If you did not make this request, you may simply ignore it.
	"""

	mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to reset your password')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', category='warning')
		return redirect(url_for('reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #decode part just turns the hashed pw bytes into a string
		user.password = hashed_pw
		db.session.commit()

		#Flashes a message to let us know the post request was successful
		flash('Your password has been updated!', category='success')
		return redirect(url_for('login'))
	return render_template('reset_password.html', title='Reset Password', form=form)