APP=uelc
JS_FILES=media/js/uelc_admin
PY_DIRS=$(APP) gate_block curveball features
MAX_COMPLEXITY=9

all: jenkins

include *.mk

travis: jenkins integration

integration: check
	$(MANAGE) jenkins --settings=$(APP).settings_integration

behave: check
	$(MANAGE) behave features/
