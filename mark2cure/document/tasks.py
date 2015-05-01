from django.conf import settings

from mark2cure.document.models import Document, Pubtator, Section
from mark2cure.common.formatter import pad_split

from Bio import Entrez, Medline
from celery import task

import requests
from datetime import datetime, timedelta
import time


@task()
def check_pubtator_responses():
    for pubtator_pk in Pubtator.objects.filter(validate_cache=False).value_list('pk', flat=True):
        get_pubtator_response(pubtator_pk)


@task()
def get_pubtator_response(pk):
    pubtator = Pubtator.objects.get(pk=pk)

    if pubtator.session_id:
        # Make response to post job to pubtator
        payload = {'content-type': 'text/xml'}
        writer = pubtator.document.as_writer()
        data = str(writer)
        url = 'http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/{session_id}/Receive/'.format(
            session_id=pubtator.session_id)

        results = requests.post(url, data=data, params=payload)
        pubtator.request_count = pubtator.request_count + 1

        if results.content != 'Not yet':
            pubtator.content = results.text

        pubtator.save()


@task()
def get_pubmed_document(pubmed_ids, include_pubtator=True):
    Entrez.email = settings.ENTREZ_EMAIL

    if type(pubmed_ids) == list:
        ids = [str(doc_id) for doc_id in pubmed_ids]
    else:
        ids = [str(pubmed_ids)]

    h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
    records = Medline.parse(h)

    # Reference to abbreviations: http://www.nlm.nih.gov/bsd/mms/medlineelements.html
    for record in records:
        if record.get('TI') and record.get('AB') and record.get('PMID') and record.get('CRDT'):
            #if Document.objects.pubmed_count(record.get('PMID')) is 0:
            title = ' '.join( pad_split(record.get('TI')) )
            abstract = ' '.join( pad_split(record.get('AB')) )

            print title

            doc, doc_c = Document.objects.get_or_create(document_id=record.get('PMID'))
            doc.title = title
            doc.source = 'pubmed'
            doc.save()

            sec, sec_c = Section.objects.get_or_create(kind='t', document=doc)
            sec.text = title
            sec.save()

            sec, sec_c = Section.objects.get_or_create(kind='a', document=doc)
            sec.text = abstract
            sec.save()

            if include_pubtator:
                doc.init_pubtator()




@task
def get_pubmed_documents(terms=settings.ENTREZ_TERMS):
    Entrez.email = settings.ENTREZ_EMAIL

    for term in terms:
        h = Entrez.esearch(db='pubmed', retmax=settings.ENTREZ_MAX_COUNT, term=term)
        result = Entrez.read(h)
        ids = result['IdList']
        get_pubmed_document(ids)

