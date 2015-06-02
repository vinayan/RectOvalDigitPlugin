#!/usr/bin/env bash
LOCALES=$*

for LOCALE in ${LOCALES}
  do
    echo "i18n/"${LOCALE}".ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    pylupdate4 -noobsolete ${PYTHON_FILES} -ts i18n/${LOCALE}.ts
done

