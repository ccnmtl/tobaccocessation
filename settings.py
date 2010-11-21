from settings_shared import *

#DATABASE_ENGINE = 'sqlite3' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres'
#DATABASE_NAME = 'blackrock_portal'
DATABASE_NAME = 'blackrock'
GDAL_LIBRARY_PATH = '/Library/Frameworks/GDAL.framework/unix/lib/libgdal.dylib'
GEOS_LIBRARY_PATH = '/Library/Frameworks/GEOS.framework/unix/lib/libgeos_c.dylib'
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/core2' 


MEDIA_ROOT = "/Users/sdreher/Documents/workspace/blackrock/uploads/"
