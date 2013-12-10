from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User

from boto.mturk.connection import *
from boto.mturk.question import *
from boto.mturk.qualification import *

import requests, datetime, random, re, nltk

def get_mturk_account(worker_id):
    u, created = User.objects.get_or_create(username=worker_id)
    if created:
        u.set_password('')
        profile = u.profile
        profile.email_notify = False
        profile.mturk = True
        profile.save()
        u.save()

    return u



def get_timezone_offset(tz):
    offset = datetime.now(tz).strftime('%z')

    sign = 1
    if offset[0] == '-':
        sign = -1

    return sign * float(offset[1:]) / 100

'''
  Text Utility Functions

'''

def is_negative(text):
    return False


def text_has_link(text):
    pattern = re.compile("(https?://|a href)")
    match = pattern.findall(text, re.I)
    return True if len(match) else False


def text_has_any_words(text, words):
    for word in text.split():
        if word in words:
            return True

    return False


def text_has_any_string(text, strings):
    for string in strings:
        if string in text:
            return True

    return False


def text_has_any_pattern(text, patterns):
    combined = "(" + "|".join(patterns) + ")"
    if re.match(combined, text):
        return True
    return False


'''
  Language Utilities
'''

def tokenize(text):
    try:
        return nltk.word_tokenize(text)
    except Exception, e:
        print e
        return text.split()

def pos_tag(text):
    tokens = tokenize(text)
    try:
        return nltk.pos_tag(tokens)
    except Exception:
        tags = []
        for word in tokens:
            tags.append((word, '???'))

        return tags


def get_proper_nouns(text):
    pos_tags = pos_tag(text)
    return [word for word,pos in pos_tags if pos == 'NNP']


def language_clean(text):
    text = text.strip()
    # text.delete!("\"") if text.count("\"").odd? # derp, we have an unmatched quote? -- let's remove ALL the quotes!
    # text.gsub!(/\A\)[\.\s]/, "") # dumbass parens
    # text = text.strip.strip_html.squeeze(" ").gsub(/\.{4,}/,
    # "...").gsub(/(\r|\n|\t)/," ").gsub(/\?{2,}/, "?").gsub(/\!{2,}/, "!")
    return text


def clean_spaces(text):
    return ' '.join(text.split()).strip()


def is_question(text):
    return '?' in text.strip()[-3:]


def is_respondable(text):
    return True

'''
  AWS Stuff
  ---------

  Helper methods for creating HITs, Qualifications
'''

class Turk():

  def __init__(self):
    self.mtc = MTurkConnection( aws_access_key_id = settings.AWS_ACCESS_ID,
                                aws_secret_access_key = settings.AWS_SECRET_KEY,
                                host = settings.AWS_HOST)

  # Utility Methods
  def disable_all(self):
      for hit in self.mtc.get_all_hits():
          self.mtc.disable_hit( hit.HITId )

  def ban_user(self, worker_id, reason="Did not meet our standards."):
      self.mtc.block_worker(worker_id, reason)

  def external_question(self, doc_id):
      # Would be cool to pull the length of the document to know the correct size of the window to show
      return ExternalQuestion("https://mark2cure.org/document/"+str(doc_id), 800)

  def make_qualification_test(self):
      '''
        This qualification type only gets created once and is what is shown to
        new workers before answering any questions

      '''
      # Define question form
      question_form = QuestionForm()

      #
      # Instructions to train the Worker
      #
      overview = Overview()
      overview.append_field('Title', 'Instructions')
      overview.append(FormattedContent( '<p><strong>Task:</strong> You will be presented with text from the biomedical literature which we believe may help resolve some important medical related questions. The task is to highlight words and phrases in that text which are <u>diseases</u>, <u>disease groups</u>, or <u>symptoms</u> of diseases.  <u>This work will help advance research in cancer and many other diseases</u>!</p>'
                                        '<p><strong>Here are some examples of correctly highlighted text.  Please study these before attempting to take the qualification test.  Please also feel free to refer back to these examples if you are uncertain.</strong></p>'
                                        '<h2>Instructions</h2>'
                                        '<ol>'
                                          '<li>'
                                            '<h3>Highlight <u>all</u> diseases and disease abbreviations</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                          '<li>'
                                            '<h3>Highlight the longest span of text specific to a disease</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                          '<li>'
                                            '<h3>Highlight disease conjunctions as single, long spans.</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                          '<li>'
                                            '<h3>Highlight symptoms - physical results of having a disease</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                          '<li>'
                                            '<h3>Highlight <u>all</u> occurrences of disease terms</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                          '<li>'
                                            '<h3>Highlight <u>all</u> diseases, disease groups and key disease symptoms</h3>'
                                            '<img alt="TODO" src="https://mark2cure.org/img/experiment/3/instructions/6.gif" />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                            '<br />'
                                          '</li>'
                                        '</ol>'))

      #
      # Questions to ask the Worker
      #
      instructions = "Select all and only the terms that should be highlighted for each text segment (don't select terms that overlap with each other in the text):"

      # Question 1
      qc = QuestionContent()
      qc.append_field('Title', instructions)
      qc.append_field('Text', "Myotonic dystrophy ( DM ) is associated with a ( CTG ) n trinucleotide repeat expansion in the 3-untranslated region of a protein kinase-encoding gene , DMPK , which maps to chromosome 19q13 . 3 . ")

      # Make question choices
      s1 = ("Myotonic", "A")
      s2 = ("dystrophy", "B")
      s3 = ("Myotonic dystrophy", "C")
      s4 = ("DM", "D")
      s5 = ("CTG", "E")
      s6 = ("trinucleotide repeat expansion", "F")
      s7 = ("DMPK", "G")

      choices = SelectionAnswer(
          style='multichooser',
          max=2,
          selections=[s1, s2, s3, s4, s5, s6, s7])

      # Define question
      q1 = Question(identifier = 'term_selection_1',
                    content = qc,
                    answer_spec = AnswerSpecification(choices),
                    is_required = True)

      # Question 2
      qc = QuestionContent()
      qc.append_field('Title', instructions)
      qc.append_field('Text', "Germline mutations in BRCA1 are responsible for most cases of inherited breast and ovarian cancer . However , the function of the BRCA1 protein has remained elusive . As a regulated secretory protein , BRCA1 appears to function by a mechanism not previously described for tumour suppressor gene products.")

      # Make question choices
      s1 = ("Germline mutations", "H")
      s2 = ("inherited breast and ovarian cancer", "I")
      s3 = ("breast", "J")
      s4 = ("ovarian cancer", "K")
      s5 = ("cancer", "L")
      s6 = ("tumour", "M")
      s7 = ("tumour suppressor", "N")

      choices = SelectionAnswer(
          style='multichooser',
          max=2,
          selections=[s1, s2, s3, s4, s5, s6, s7])

      # Define question
      q2 = Question(identifier = 'term_selection_2',
                    content = qc,
                    answer_spec = AnswerSpecification(choices),
                    is_required = True)



      # Question 3
      qc = QuestionContent()
      qc.append_field('Title', instructions)
      qc.append_field('Text', "We report about Dr . Kniest , who first described the condition in 1952 , and his patient , who , at the age of 50 years is severely handicapped with short stature , restricted joint mobility , and blindness but is mentally alert and leads an active life .  This is in accordance with molecular findings in other patients with Kniest dysplasia and...")

      # Make question choices
      s1 = ("age of 50 years", "O")
      s2 = ("short stature", "P")
      s3 = ("restricted joint mobility", "Q")
      s4 = ("severely handicapped", "R")
      s5 = ("short", "S")
      s6 = ("blindness", "T")
      s7 = ("dysplasia", "U")
      s8 = ("Kniest dysplasia", "V")
      s9 = ("molecular findings", "W")

      choices = SelectionAnswer(
          style='multichooser',
          max=5,
          selections=[s1,s2,s3,s4, s5, s6, s7, s8, s9])

      # Define question
      q3 = Question(identifier = 'term_selection_3',
                    content = qc,
                    answer_spec = AnswerSpecification(choices),
                    is_required = True)

      # Add the content to the questionform
      question_form.append(overview)
      question_form.append(q1)
      question_form.append(q2)
      question_form.append(q3)

      # Define evaluation mechanism
      answer_logic = '''<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">

                          <Question>
                          <QuestionIdentifier>term_selection_1</QuestionIdentifier>
                            <AnswerOption>
                              <SelectionIdentifier>C</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>D</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                          </Question>

                          <Question>
                          <QuestionIdentifier>term_selection_2</QuestionIdentifier>
                            <AnswerOption>
                              <SelectionIdentifier>I</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>M</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                          </Question>

                          <Question>
                          <QuestionIdentifier>term_selection_3</QuestionIdentifier>
                            <AnswerOption>
                              <SelectionIdentifier>P</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>Q</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>R</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>T</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                            <AnswerOption>
                              <SelectionIdentifier>V</SelectionIdentifier>
                              <AnswerScore>1</AnswerScore>
                            </AnswerOption>
                          </Question>

                          <PercentageMapping>
                            <MaximumSummedScore>9</MaximumSummedScore>
                          </PercentageMapping>
                        </AnswerKey>'''

      qual_test = self.mtc.update_qualification_type(settings.AWS_QUAL_TEST_3,
      # qual_test = self.mtc.create_qualification_type(
        # name = 'Annotation Instructions & Qualification Questions',
        description = 'Detailed annotation instructions. Multiple-choice questions to assess concept understanding.',
        status = 'Active',
        test = question_form,
        # answer_key = answer_logic,
        retry_delay = 1,
        test_duration = 20 * 60)

      return qual_test

  # Actionable methods
  def hit_for_document(self, doc_id, max_assignments = 5, reward = 0.06, minutes = 4, title="Highlight diseases in paragraph"):
      description = ('Highlight by clicking or dragging over multiple words in the following paragraph that are diseases. Do *not* select symptoms, conditions or any other non-disease term. When available, highlight multi-word disease together by click and dragging. When you accept the HIT, you will be allowed to start highlighting and a submit button will appear.')
      keywords = 'science, annotation, disease, text, highlight, annotation, medicine, term recognition'

      qualifications = Qualifications()
      # Add the step instructions and basic test
      qualifications.add( Requirement(settings.AWS_QUAL_TEST_3, "GreaterThanOrEqualTo", 6) )

      hit = self.mtc.create_hit(
          hit_type = None,
          question = self.external_question(doc_id),
          hit_layout = None,
          lifetime = datetime.timedelta(7),
          max_assignments = max_assignments,
          title = title,
          description = description,
          keywords = keywords,
          reward = reward,
          duration = datetime.timedelta(minutes = minutes),
          approval_delay = None,
          annotation = None,
          questions = None,
          qualifications = qualifications,
          layout_params = None,
          response_groups = None
          )
      return hit
