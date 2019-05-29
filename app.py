from flask import Flask,request,render_template,flash,redirect,url_for,session,logging
from wtforms import Form, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from flask_mysqldb import MySQL


app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='databasename'
app.config['MYSQL_CURSORCLASS']='DictCursor'


mysql=MySQL(app)

#textcomments is the name of the table so just change it in all the places ;)
class comments():
    def gettcomm(id):
        cur = mysql.connection.cursor()
        cur.execute("""
			SELECT  UserComment.*, (COUNT(Ghost.id) - 1) AS depth
			FROM (textcomments AS UserComment, textcomments as Ghost)
								    
			WHERE	UserComment.lft BETWEEN Ghost.lft AND Ghost.rgt
			AND		Ghost.post_id = %s
			AND		UserComment.post_id =%s
			AND		UserComment.parent_id is not null
								
			GROUP BY UserComment.id
			ORDER BY UserComment.lft""", ([id], [id]))
        commentaria = cur.fetchall()
        cur.close()
        return commentaria
        
class commentform(Form):
    comment = StringField(validators = [validators.required(), validators.Length(max=1000)])

@app.route("/post/<string:id>/<title>", methods=['GET', 'POST'])
def post(id, title):
    form = commentform(request.form)
    cur = mysql.connection.cursor()
    r = cur.execute("SELECT * FROM posts WHERE ID=%s AND title=%s", [id, title])
    post = cur.fetchone()
    if r==0:
        flash("no post found with that id")
        return redirect(url_for('index'))
    if 'logged_in' in session :
        if (request.method == 'POST' and form.validate()):
            parent_id = request.form['parent_id']
            comment = form.comment.data
            if parent_id == '0':
                g = cur.execute("SELECT * FROM textcomments WHERE post_id=%s AND parent_id=0", [id])
                if g ==0:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO textcomments (text, username, post_id,parent_id, lft, rgt) VALUES (%s, %s, %s, %s, '1', '2')", (comment, session['username'], id,parent_id))
                    mysql.connection.commit()
                    cur.close()
                    flash("Comment successful", 'success')
                    return redirect(url_for('indx'))
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT rgt, lft FROM textcomments WHERE post_id = %s AND parent_id=0", [id])
                    k = cur.fetchall()
                    for row in k:
                        rgt = row["rgt"] + 2
                        lft = row["rgt"] + 1
                    cur.execute("INSERT INTO textcomments (text, username, post_id,parent_id, lft, rgt) VALUES (%s, %s, %s, %s, %s, %s)", (comment, session['username'], id,parent_id, lft, rgt))
                    mysql.connection.commit()
                    cur.close()
                    flash("Comment successful", 'success')
                    return redirect(url_for('indx'))
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO textcomments (text, username, post_id,parent_id) VALUES (%s, %s, %s, %s)", (comment, session['username'], id,parent_id))
                lastinsertedid= cur.lastrowid
                cur.execute("SELECT @myRight := rgt FROM textcomments WHERE id = %s", [parent_id])
                cur.execute("UPDATE textcomments SET lft = lft + 2 WHERE post_id = %s AND lft >= @myRight", [id])
                cur.execute("UPDATE textcomments SET rgt = rgt + 2 WHERE post_id = %s AND rgt >= @myRight", [id])
                cur.execute("UPDATE textcomments SET lft = @myRight WHERE id = %s", [lastinsertedid])
                cur.execute("UPDATE textcomments SET rgt = @myRight + 1 WHERE id = %s", [lastinsertedid])
                mysql.connection.commit()
                cur.close()
                flash("Comment successful", 'success')
                return redirect(url_for('indx'))

    commentaria = comments.gettcomm(id)
    return render_template('post.html' , post = post, form=form, commentaria=commentaria)
