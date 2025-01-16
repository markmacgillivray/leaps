SECRET_KEY = "default-key" # make this something secret in your overriding app.cfg

# contact info
ADMIN_NAME = "LEAPS"
ADMIN_EMAIL = "m@leviathan.sh"
LEAPS_EMAIL = "leapspae@ed.ac.uk"

# service info
SERVICE_NAME = "LEAPS"
HOST = "0.0.0.0"
DEBUG = True
PORT = 5005

# list of superuser account names
SUPER_USER = ["test"]
CREATE_SUPER_USER = False # whether or not to create the superuser account if it does not exist (and if initialising the index, see below)
PUBLIC_REGISTER = False # Can people register publicly? If false, only the superuser can create new accounts

# elasticsearch settings
ELASTIC_SEARCH_HOST = "http://127.0.0.1:9200"
ELASTIC_SEARCH_DB = "leaps"
INITIALISE_INDEX = False # whether or not to try creating the index and required index types on startup
NO_QUERY_VIA_API = ['account','student'] # list index types that should not be queryable via the API


FACET_FIELD = ".keyword" # identifier for how non-analyzed fields for faceting are differentiated in the mappings
# dict of ES mappings, settings, aliases if necessary. identify index by key name. Put the mapping in a "mapping" key. 
# if no settings mappings or aliases are needed for a type, set the value to {}
# otherwise provide any needed as per https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html
MAPPINGS = {"student" : {}}
MAPPINGS['account'] = MAPPINGS["student"] # if needed to just copy a mapping to another index, do like this
MAPPINGS['school'] = {}
MAPPINGS['subject'] = {}
MAPPINGS['advancedsubject'] = {}
MAPPINGS['level'] = {}
MAPPINGS['grade'] = {}
MAPPINGS['institution'] = {}
MAPPINGS['advancedlevel'] = {}
MAPPINGS['archive'] = {}
MAPPINGS['simd'] = {}

#UPLOAD_DATA = {} # key should match an index name above, and value should be the file location to bulk upload
UPLOAD_DATA = {
  #"student" : "/home/leaps/MOVE/leaps/leaps_student.json",
  #"account" : "/home/leaps/MOVE/leaps/leaps_account.json",
  #"school" : "/home/leaps/MOVE/leaps/leaps_school.json",
  #"subject" : "/home/leaps/MOVE/leaps/leaps_subject.json",
  #"advancedsubject" : "/home/leaps/MOVE/leaps/leaps_advancedsubject.json",
  #"level" : "/home/leaps/MOVE/leaps/leaps_level.json",
  #"grade" : "/home/leaps/MOVE/leaps/leaps_grade.json",
  #"institution" : "/home/leaps/MOVE/leaps/leaps_institution.json",
  #"advancedlevel" : "/home/leaps/MOVE/leaps/leaps_advancedlevel.json",
  #"archive" : "/home/leaps/MOVE/leaps/leaps_archive.json",
  #"simd" : "/home/leaps/MOVE/leaps/leaps_simd.json"
}
#UPLOAD_EMPTY_FIRST = {} key should match an index with value True if index should be emptied before upload - and only happens if in UPLOAD_DATA
UPLOAD_EMPTY_FIRST = {
  #"student" : True,
  #"account" : True,
  #"school" : True,
  #"subject" : True,
  #"advancedsubject" : True,
  #"level" : True,
  #"grade" : True,
  #"institution" : True,
  #"advancedlevel" : True,
  #"archive" : True,
  #"simd" : True
}