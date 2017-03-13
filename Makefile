APP=tobaccocessation
JS_FILES=media/js/util.js media/prescription/js/  media/virtualpatient/js/
MAX_COMPLEXITY=7

all: jenkins

include *.mk

eslint: $(JS_SENTINAL)
	$(NODE_MODULES)/.bin/eslint $(JS_FILES)

.PHONY: eslint
