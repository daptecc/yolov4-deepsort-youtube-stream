from flask import render_template, flash, redirect, url_for, Response, request
from app import app
from app.forms import URLForm
from app.videostream import VideoStream

#https://www.youtube.com/watch?v=iQvSrXIpw1k

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title = 'Home')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = URLForm()
    if form.validate_on_submit():
        url=request.form['url']
        if url != None:
            return redirect(url_for('stream', url = url))
        else:
            return redirect(url_for('search'))

    return render_template('search.html', title='Grab Video', form=form)

@app.route('/stream', methods=['GET'])
def stream():    
    userStream = request.args.get('url')
    return Response(VideoStream(userStream).process_stream(),
    #return Response(VideoStream(userStream).streamRawVideo(),
    mimetype='multipart/x-mixed-replace; boundary=frame')
