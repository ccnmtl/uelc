APP=uelc
JS_FILES=media/js/uelc_admin media/ckeditor/ckeditor/plugins/awsimage/
PY_DIRS=$(APP) gate_block curveball features
MAX_COMPLEXITY=7

all: jenkins

include *.mk

travis: integration

integration: check
	$(MANAGE) test --settings=$(APP).settings_integration

behave: check
	$(MANAGE) behave

eslint: $(JS_SENTINAL)
	$(NODE_MODULES)/.bin/eslint $(JS_FILES)

.PHONY: eslint
