from flask import request, jsonify
from flask.ext.restful import reqparse, Resource
from flask_login import login_user, current_user
from flask_mail import Message

# from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql.expression import ClauseElement
# from collections import OrderedDict

from ..models import User, Document, Annotation, View
from ..core import db, mail
from mark2cure.settings import *
from mark2cure.manage.analysis import user_vs_gold
from mark2cure.manage.aws import Turk

document_parser = reqparse.RequestParser()
document_parser.add_argument('document_id',   type=int,   location='json')
document_parser.add_argument('title',         type=str,   location='json')
document_parser.add_argument('annotations',   type=list,  location='json')

# Will only ever GET from Documents to initialize
# Will only ever PUT to Documents to add annotations
# Will serve 'heatmap' models in fetch based on word index sums

class Documents(Resource):
    def get(self, doc_id=None):
        if doc_id:
          document = db.session.query(Document).get(doc_id)
          return jsonify(objects=[document.json_view(current_user)])
        else:
          documents = Document.query.limit(30).all()
          return jsonify(objects=[i.json_view(current_user) for i in documents])

    def put(self, doc_id):
        args = document_parser.parse_args()
        document = Document.query.get(doc_id)
        env =  request.environ

        view = View(current_user, document);
        db.session.add(view)
        db.session.commit()

        for ann in args['annotations']:
          ann = Annotation( ann['kind'],
                            ann['type'],
                            ann['text'],
                            ann['start'],
                            ann['length'],
                            ann['stop'],
                            current_user,
                            document,
                            env.get('HTTP_USER_AGENT'),
                            env.get('REMOTE_ADDR'),
                            None
                          );
          db.session.add(ann)
        db.session.commit()

        if current_user.mturk:
            # Just email me for fun...
            msg = Message(recipients=["dragon@puff.me.uk"],
                          subject="MTurk Submission")
            mail.send(msg)

        # Check document and mturk status
        if document.validate and current_user.mturk:
            truth = user_vs_gold(current_user, document)
            score = 1 if truth[0] > 0 else 0
            t = Turk()
            t.mtc.update_qualification_score(AWS_QUAL_GM_SCORE, current_user.username, score)

        return args, 201
