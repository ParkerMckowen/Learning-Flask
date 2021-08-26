from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SCApp.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm_password', validators=[EqualTo('password')])
	submit = SubmitField('Sign Up')

	# Format to make a custom validator
	#----------------------------------
	# def validate_field(self, field):
	# 	if True:
	# 		raise ValidationError('Validation Message')

	def validate_username(self, username):
		# Query returns None if there is no match to the entered username
		match = User.query.filter_by(username=username.data).first()

		if match:
			raise ValidationError('Username already exists.')

	def validate_email(self, email):
		# Query returns None if there is no match to the entered email
		match = User.query.filter_by(email=email.data).first()

		if match:
			raise ValidationError('Email already exists')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remeber Me?')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	# Format to make a custom validator
	#----------------------------------
	# def validate_field(self, field):
	# 	if True:
	# 		raise ValidationError('Validation Message')

	def validate_username(self, username):
		if username.data != current_user.username: # takes care of scenario where user does not update anything
			# Query returns None if there is no match to the entered username
			match = User.query.filter_by(username=username.data).first()

			if match:
				raise ValidationError('Username already exists.')

	def validate_email(self, email):
		if email.data != current_user.email: # takes care of scenario where user does not update anything
			# Query returns None if there is no match to the entered email
			match = User.query.filter_by(email=email.data).first()

			if match:
				raise ValidationError('Email already exists')


class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Create Post')

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')


	def validate_email(self, email):
		# Query returns None if there is no match to the entered email
		match = User.query.filter_by(email=email.data).first()

		if match is None:
			raise ValidationError('Email does not exist')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm_password', validators=[EqualTo('password')])
	submit = SubmitField('Reset Password')