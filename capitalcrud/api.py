# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from capitalcrud import get_model, oauth2, storage, tasks
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for, jsonify, make_response


#@app.errorhandler()
#def not_found(error):
#    return make_response(jsonify({'error': 'Not found'}), 404)

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def list():
    #TODO TEST query=country:Paris
    q = request.args.get('query')
    if q:
        query_params={}
        query_params['prop'], query_params['value'] = q.split(":")
    else:
        query_params=None
        
    #TODO search=Antartica
    s = request.args.get('search')
    if not s:
        s = None
            
    capitals, next_page_token = get_model().list(limit=None, cursor=None, query_params=query_params, search_params=s)
    
    return jsonify( {'capitals': capitals} )


@api.route('/<id>', methods=['GET'])
def view(id):
    capital = get_model().read(id)    
    return jsonify(capital)


@api.route('/<id>', methods=['PUT'])
def update(id):
    try:
        capital = get_model().update(data, id)
        data = request.form.to_dict(flat=True)
 #      q = tasks.get_capitals_queue()
 #      q.enqueue(tasks.process_capital, capital['id'])

        return make_response("",200)
    except:
        return make_response(jsonify({"error": { "code": "500", "message": "Unexepected error" }}))

@api.route('/<id>', methods=['DELETE'])
def delete(id):
    try:
        get_model().delete(id)
        return make_response("",200)
    except:
        #TODO need to check if the id exists first and return error or get it from an exception?
        return make_response(jsonify({"error": { "code": "500", "message": "Unexepected error" }}))

@api.route('<id>/publish', methods=['POST'])
def publish(id):
    #TODO finish - push to pubsub and return pubsub id
    """
    Input:
        Topic {
            topic: string
        }

    Returns: 
        TopicResponse {
            messageId: number
        }
    or
    
        return make_response(jsonify({"error": { "code": "500", "message": "Unexepected error" }}))
   
    """
@api.route('<id>/store')
def store(id):
    #TODO finish - store to GCS 
    """
    inputs:
    id
    
    Storage {
        bucket: string
    }
    
    returns:
    200
    or
        return make_response(jsonify({"error": { "code": "500", "message": "Unexepected error" }}))
    """
    
    
    
    
    
"""
@api.route("/mine")
@oauth2.required
def list_mine():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    capitals, next_page_token = get_model().list_by_user(
        user_id=session['profile']['id'],
        cursor=token)

    return render_template(
        "list.html",
        capitals=capitals,
        next_page_token=next_page_token)

@api.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If an image was uploaded, update the data to point to the new image.
        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        # If the user is logged in, associate their profile with the new capital.
        if 'profile' in session:
            data['createdBy'] = session['profile']['displayName']
            data['createdById'] = session['profile']['id']

        capital = get_model().create(data)

        # [START enqueue]
        q = tasks.get_capitals_queue()
        q.enqueue(tasks.process_capital, capital['id'])
        # [END enqueue]

        return redirect(url_for('.view', id=capital['id']))

    return render_template("form.html", action="Add", capital={})


@api.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    capital = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        capital = get_model().update(data, id)

        q = tasks.get_capitals_queue()
        q.enqueue(tasks.process_capital, capital['id'])

        return redirect(url_for('.view', id=capital['id']))

    return render_template("form.html", action="Edit", capital=capital)


@api.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))
"""
