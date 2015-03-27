from django.conf import settings

from .s3boto import S3BotoStorage, SubdomainCallingFormat, S3Connection


def get_setting(_settings, name, default=None):
    """
    Helper function to get a Django setting by name or (optionally) return
    a default (or else ``None``).
    """
    if isinstance(_settings, dict):
        return _settings.get(name, default)
    return getattr(_settings, name, default)

SETTINGS_DICT = getattr(settings, 'STORAGES_S3BOTO_MULTI', {})
for s3store in SETTINGS_DICT:

    # Wrap class definition inside function closure to avoid conflicts between custom instances
    def init_s3boto_storage_custom(class_name):

        setting = lambda name, default=None: get_setting(SETTINGS_DICT[s3store], name, default)

        class S3BotoStorageCustom(S3BotoStorage):
            """
            S3 storage backend that looks for custom settings in STORAGES_CUSTOM_AWS_*
            """
            # TODO: move to fabric dictionary
            # used for looking up the access and secret key from env vars
            access_key_names = ['AWS_S3_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID']
            secret_key_names = ['AWS_S3_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY']

            access_key = setting('AWS_S3_ACCESS_KEY_ID', setting('AWS_ACCESS_KEY_ID'))
            secret_key = setting('AWS_S3_SECRET_ACCESS_KEY', setting('AWS_SECRET_ACCESS_KEY'))
            file_overwrite = setting('AWS_S3_FILE_OVERWRITE', True)
            headers = setting('AWS_HEADERS', {})
            bucket_name = setting('AWS_STORAGE_BUCKET_NAME')
            auto_create_bucket = setting('AWS_AUTO_CREATE_BUCKET', False)
            default_acl = setting('AWS_DEFAULT_ACL', 'public-read')
            bucket_acl = setting('AWS_BUCKET_ACL', default_acl)
            querystring_auth = setting('AWS_QUERYSTRING_AUTH', True)
            querystring_expire = setting('AWS_QUERYSTRING_EXPIRE', 3600)
            reduced_redundancy = setting('AWS_REDUCED_REDUNDANCY', False)
            location = setting('AWS_LOCATION', '')
            encryption = setting('AWS_S3_ENCRYPTION', False)
            custom_domain = setting('AWS_S3_CUSTOM_DOMAIN')
            calling_format = setting('AWS_S3_CALLING_FORMAT', SubdomainCallingFormat())
            secure_urls = setting('AWS_S3_SECURE_URLS', True)
            file_name_charset = setting('AWS_S3_FILE_NAME_CHARSET', 'utf-8')
            gzip = setting('AWS_IS_GZIPPED', False)
            preload_metadata = setting('AWS_PRELOAD_METADATA', False)
            gzip_content_types = setting('GZIP_CONTENT_TYPES', (
                'text/css',
                'text/javascript',
                'application/javascript',
                'application/x-javascript',
            ))
            url_protocol = setting('AWS_S3_URL_PROTOCOL', 'http:')
            host = setting('AWS_S3_HOST', S3Connection.DefaultHost)
            use_ssl = setting('AWS_S3_USE_SSL', True)
            port = setting('AWS_S3_PORT', None)

            # The max amount of memory a returned file can take up before being
            # rolled over into a temporary file on disk. Default is 0: Do not roll over.
            max_memory_size = setting('AWS_S3_MAX_MEMORY_SIZE', 0)

        return type(class_name, (S3BotoStorageCustom,), {})

    # Populate the module namespace with our custom initialized S3BotoStorageCustom
    # class giving it a name of S3BotoStorage_name where name is the dict key given
    # in the settings.
    class_name = 'S3BotoStorage_' + s3store
    globals()[class_name] = init_s3boto_storage_custom(class_name)
