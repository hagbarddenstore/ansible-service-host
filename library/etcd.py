#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.basic import *

import urllib
import urllib2
import json

DOCUMENTATION = '''
'''

EXAMPLES = '''
'''

class RequestWithMethod(urllib2.Request):
    def __init__(self, *args, **kwargs):
        self._method = kwargs.pop('method', None)

        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)

def get_key(host, key):
    try:
        r = RequestWithMethod(
            method='GET',
            url=get_url(host, key)
        )

        f = urllib2.urlopen(r)

        j = json.load(f)

        return j['node']['value']
    except urllib2.HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise

def set_key(host, key, value):
    r = RequestWithMethod(
        method='PUT',
        url=get_url(host, key),
        data=urllib.urlencode({'value': value})
    )

    f = urllib2.urlopen(r)

    # TODO: Figure out what to return...
    return True

def delete_key(host, key):
    try:
        r = RequestWithMethod(
            method='DELETE',
            url=get_url(host, key)
        )

        f = urllib2.urlopen(r)

        # TODO: Figure out what to return...
        return True
    except urllib2.HTTPError as e:
        if e.code == 404:
            return False
        else:
            raise

def get_url(host, key):
    return "%s/v2/keys/%s" % (host.rstrip('/'), key.lstrip('/'))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            host=dict(required=False, default='http://127.0.0.1:2379'),
            key=dict(required=True),
            value=dict(required=False, default=None)
        ),
        supports_check_mode=True
    )

    state = module.params['state']
    host = module.params['host']
    key = module.params['key']
    value = module.params.get('value', '')

    #module.fail_json(msg=value)

    prev_value = None

    try:
        prev_value = get_key(host, key)
    except Exception as error:
        module.fail_json(msg=repr(error))

    try:
        if state == 'present' and not value:
            module.fail_json(msg='value is required with state="present"')

        if state == 'present':
            if prev_value == value:
                module.exit_json(
                    changed=False,
                    prev_value=prev_value,
                    value=value,
                    key=key
                )
            else:
                changed = set_key(host, key, value)

                module.exit_json(
                    changed=changed,
                    prev_value=prev_value,
                    value=value,
                    key=key
                )
        else:
            changed = delete_key(host, key)

            module.exit_json(
                changed=changed,
                prev_value=prev_value,
                key=key
            )
    except Exception as error:
        module.fail_json(msg=repr(error))

main()
