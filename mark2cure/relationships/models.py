'''
Sets up the models for the relationship application, modeled after Max's
Document/models.py file for standardization and using Toby's data_model.py

Most of this code is Toby's, but reconfigured to work in the Django app, where
tasks.py performs much of the actions involved in populating the new documents
(pmid) into the database.

'''
import datetime
from django.db import models
from django.utils import timezone


class Paper(models.Model):
    """
    snip of the Max's document section in the database administration:
    Document id
    Title preview    Sections   Pubtator   Annotations   Completed views    Pending   views  Source
	22206664	The Nogo receptor 2 is a novel substrate of Fbs1 .	2	True	82	12	2	group5

    """
    """
    A single academic publication.
    Contains:
    1. The PubMed identifier.
    2. The title as a string.
    3. The abstract as a string.
    4. A list of all chemical and disease annotations in the title and abstract
       sorted in increasing order of starting index.
    5. A potentially empty list of gold standard CID relations.
    6. A set of unique chemical identifiers.
    7. A set of unique disease identifiers.
    8. A list of Sentences containing both the title and body of the abstract.
       The first sentence is the title. Each sentence contains the annotations
       and relations constrained to that particular sentence.
    9. A set of all the potential chemical-disease relations grouped into three
       mutually exclusive categories:
            - CID relations
            - Non-CID sentence-bound relations
            - Non-sentence bound relations
            The sum of relations in all three groups should equal the number of
            unique chemical IDs times the number of unique disease IDs.
    """
    #def __init__(self, pmid, title, abstract, annotations, gold_relations = []):
    # 1
    pmid = models.TextField(blank=False)
    # 2
    title = models.TextField(blank=False)
    # 3
    abstract = models.TextField(blank=False)
    # 4
    #annotations = sorted(annotations)
    annotations = models.TextField(blank=False) # LIST TODO
    #gold_relations = models.TextField(blank=False) # TODO check what false is here
    #assert self._has_correct_annotations() TODO add back
    # 5
    #gold_relations = models.TextField(blank=False) # may be empty when not parsing gold # LIST TODO
    # 6 & 7

    #chemicals = models.TextField(blank=False)
    #diseases = models.TextField(blank=False)


    #chemicals, diseases = _get_unique_concepts()

    # 8 split sentences and generate sentence-bound relations
    #sentences = _split_sentences()
    # 9
    #possible_relations = _classify_relations()

    #Max's model
    """
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    """
    """
    def available_sections(self):
        return self.section_set.all()

    def count_available_sections(self):
        return self.section_set.count()
    """
    # TODO add more methods that include objects of the below classes for relationship module

    """
    # TODO fix the contributors (we want to know users that contributed to this and the below CLASSES)
    def contributors(self):
        user_ids = list(set(View.objects.filter(section__document=self, completed=True).values_list('user', flat=True)))
        return user_ids
    """
    # follows max's model
    def __unicode__(self):
        return self.pmid

    # follows Toby's model:
    """
    def __repr__(self):
        return ("<{0}>: PMID {1}. {2} annotations, {3} gold relations\n"
            "{4} unique chemical ids, {5} unique disease ids\n"
            "{6} sentences".format(self.__class__.__name__,
            self.pmid, len(self.annotations), len(self.gold_relations),
            len(self.chemicals), len(self.diseases), len(self.sentences))
        )
    """
    def _has_correct_annotations(self):
        """
        Checks that the paper's annotations match the
        stated positions in the text.
        """
        text = "{0} {1}".format(self.title, self.abstract)
        for annotation in self.annotations:
            assert text[annotation.start : annotation.stop] == annotation.text, (
                "Annotation {0} in PMID {1} does not match the text.".format(annotation, self.pmid))
        return True

    def _get_unique_concepts(self):
        """
        Determines the unique identifiers of chemicals and diseases
        belonging to this paper.

        Ignores any annotations with an identifier of -1.
        """
        res = defaultdict(set)
        for annotation in self.annotations:
            if annotation.uid != "-1":
                res[annotation.stype].add(annotation.uid)
        return (res["chemical"], res["disease"])

    def _get_all_possible_relations(self):
        """
        Returns all possible unique drug-disease combinations
        as a set for this paper.
        """
        return {(chemical_id, disease_id) for chemical_id in self.chemicals for disease_id in self.diseases}

    def _split_sentences(self):
        """
        Splits the abstract up into individual sentences,
        and determines which concept annotations reside
        within each sentence.

        Time complexity:
            O(N + M) where N is the number of sentences,
            and M is the number of annotations.
        """
        all_sentences = [self.title] + split_abstract(self.abstract)

        full_text = "{0} {1}".format(self.title, self.abstract)

        sent_idx = 0 # starting index of current sentence
        annot_idx = 0 # index of annotation that is within current sentence

        res = []
        M = len(self.annotations)
        for i, sentence in enumerate(all_sentences):
            # The sentence splitter isn't perfect. It recognizes "i.v." as a
            # sentence. Since there can be multiple instances of "sentences"
            # like "i.v." (e.g., PMID 10840460), we need to make sure that
            # we are checking for the first instance starting at the current
            # position (since find always finds the first instance otherwise).
            assert full_text.find(sentence, sent_idx) == sent_idx, (
                "PMID {0} sentence '{1}' does not match text!".format(self.pmid,
                                                                      sentence))

            sent_stop = sent_idx + len(sentence)

            start_annot = annot_idx
            while annot_idx < M and self.annotations[annot_idx].stop <= sent_stop:
                annot_idx += 1

            # should be one past
            res.append(Sentence(self.pmid, i, sentence,
                sent_idx, sent_stop, self.annotations[start_annot : annot_idx]))

            sent_idx += len(sentence) + 1 # all sentences separated by one space

        return res

    def _classify_relations(self):
        """
        Takes all the possible relations for this abstract and
        splits them into three mutually exclusive groups:
            1. CID relations, which are sentence bound
            2. Non-CID, sentence-bound relations
            3. Relations which are not sentence bound (head to abstract?) TODO
        """
        all_rels = self._get_all_possible_relations()

        cid_rels = set()
        sentence_non_cid_rels = set()
        for sentence in self.sentences:
            cid_rels |= sentence.possible_relations[True]
            sentence_non_cid_rels |= sentence.possible_relations[False]

        sentence_non_cid_rels -= cid_rels

        not_sent_bound_rels = all_rels - cid_rels - sentence_non_cid_rels

        assert cid_rels.is_disjoint(sentence_non_cid_rels)
        assert cid_rels.is_disjoint(not_sent_bound_rels)
        assert not_sent_bound_rels.is_disjoint(sentence_non_cid_rels)

        assert (len(self.chemicals) * len(self.diseases)
            == len(cid_rels | sentence_non_cid_rels | not_sent_bound_rels))

        possible_relations = {
            "CID": cid_rels,
            "sentence_non_CID": sentence_non_cid_rels,
            "not_sentence_bound": not_sent_bound_rels
        }
        return possible_relations

    def _has_relation(self, potential_relation):
        """
        Checks if the provided possible Relationship object matches any of the
        gold standard relationships for this paper.

        Note:
            It is not possible to use a set to do the checking
            operation here, because it is not possible to make
            the hashes of two objects the same when they are
            defined by be equal by the overridden equals operator
            for Relation objects.

            This solution is slow, but at least it's correct.
        """
        return potential_relation in self.gold_relations

"""

class Section(models.Model):
    SECTION_KIND_CHOICE = (
        ('t', 'title')
        ('a', 'abstract')
    )

    # kind of section it is and whether or not it has BOTH chemical and disease combinations
    # if not, then don't use it.
    kind = models.CharField(max_length=1, choices=SECTION_KIND_CHOICE)
    text = models.TextField(blank=True)

    # need the span of the sentences here for reference? numbers TODO (which program?)
    span_start = models.IntegerField()
    span_end = models.IntegerField()

    # at

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # section relates back to DOCUMENT
    document = models.ForeignKey(Document)

    # TODO add more methods (look at examples)

class Entity(models.Model):
    # Here, we are either a chemical or disease only (different than main m2c)
    ENTITY_KIND_CHOICE = (
        ('c', 'chemical'),
        ('d', 'disease'),
    )
    kind = models.CharField(max_length=1, choice=ENTITY_KIND_CHOICE)
    # need the span of the sentences here for reference? numbers TODO (which program?)
    span_start = models.IntegerField()
    span_end = models.IntegerField()

# drug induces or treats? TODO ask Toby
class Relation(models.Model):
    # N (chemicals) * M (diseases) = number of relations there will be
    '''
    From Max's Annotation MODEL:
    Text Type Start Section Username Pmid Quest Group Time ago Created
	GS28	gene_protein	672	Abstract	admin	16510524	213	622	1 day, 2 hours ago	July 29, 2015, 11:51 a.m.
    '''

    # if there is an automaded CID determination, then make sure this is not
    # flagged as a user annotation.
    # TODO add user to relationships determination class in MODELS?
    automated_cid = models.BooleanField(default=False)
    # if CID relationship automatically determined, then apply relationship choice to auto
    if automated_cid == True:
        relationship = "auto"

    # the chemical-disease relationship
    RELATIONSHIP_CHOICE = (
        ('dir', 'chemical directly contributes to disease')
        ('ind', 'chemical indirectly contributes to disease')
        ('none', 'chemical does not contribute to or cause disease')
        ('auto','chemical-induced-disease was automatically determined')
    )
    relationship = models.CharField(max_length=4, choices=RELATIONSHIP_CHOICE)

    # user confidence order 1 to 4 (where 1 is not confident and 4 is confident)
    # This value is used in scoring later
    USER_CONFIDENCE_CHOICE = (
        ('C4', "Very confident")
        ('C3', "Confident")
        ('C2', "Not too confident")
        ('C1', "Not confident at all")
    )
    user_confidence = models.CharField(max_length=1, choices=USER_CONFIDENCE_CHOICE)

    # relations relate back to section, which relates back to the document
    document = models.ForeignKey(Section)
"""
