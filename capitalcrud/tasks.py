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

import logging

from capitalcrud import get_model, storage
from flask import current_app
from google.cloud import pubsub
import psq
import requests


# [START get_capitals_queue]
def get_capitals_queue():
    client = pubsub.Client(
        project=current_app.config['PROJECT_ID'])

    # Create a queue specifically for processing capitals and pass in the
    # Flask application context. This ensures that tasks will have access
    # to any extensions / configuration specified to the app, such as
    # models.
    return psq.Queue(
        client, 'capitals', extra_context=current_app.app_context)
# [END get_capiatals_queue]


# [START process_capital]
def process_capital(capital_id):
    """
    Handles an individual capitalcrud message by looking it up in the
    model, querying the Google Books API, and updating the book in the model
    with the info found in the Books API.
    """

    model = get_model()

    capital = model.read(capital_id)

    if not capital:
        logging.warn("Could not find capital with id {}".format(capital_id))
        return

    if 'title' not in capital:
        logging.warn("Can't process capital id {} without a title."
                     .format(capital_id))
        return

    logging.info("Looking up capital with title {}".format(capital[
                                                        'title']))

    new_capital_data = query_capital_api(capital['title'])

    if not new_capital_data:
        return

    capital['title'] = new_capital_data.get('title')
    capital['author'] = ', '.join(new_capital_data.get('authors', []))
    capital['publishedDate'] = new_capital_data.get('publishedDate')
    capital['description'] = new_capital_data.get('description')

    # If the new capital data has thumbnail images and there isn't currently a
    # thumbnail for the capital, then copy the image to cloud storage and update
    # the capital data.
    if not capital.get('imageUrl') and 'imageLinks' in new_capital_data:
        new_img_src = new_capital_data['imageLinks']['smallThumbnail']
        capital['imageUrl'] = download_and_upload_image(
            new_img_src,
            "{}.jpg".format(capital['title']))

    model.update(capital, capital_id)
# [END process_capital]


# [START query_capital_api]
def query_capital_api(title):
    """
    Queries the Google Books API to find detailed information about the book
    with the given title.
    """
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params={
        'q': title
    })

    try:
        data = r.json()['items'][0]['volumeInfo']
        return data

    except KeyError:
        logging.info("No book found for title {}".format(title))
        return None

    except ValueError:
        logging.info("Unexpected response from books API: {}".format(r))
        return None
# [END queue_captail_api]


def download_and_upload_image(src, dst_filename):
    """
    Downloads an image file and then uploads it to Google Cloud Storage,
    essentially re-hosting the image in GCS. Returns the public URL of the
    image in GCS
    """
    r = requests.get(src)

    if not r.status_code == 200:
        return

    return storage.upload_file(
        r.content,
        dst_filename,
        r.headers.get('content-type', 'image/jpeg'))
