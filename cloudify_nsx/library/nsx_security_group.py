# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import nsx_common as common
from cloudify import exceptions as cfy_exc


def get_group(client_session, scopeId, name):
    raw_result = client_session.read('secGroupScope',
                                     uri_parameters={'scopeId': scopeId})

    common.check_raw_result(raw_result)

    if 'list' not in raw_result['body']:
        return None

    groups = raw_result['body']['list'].get('securitygroup')

    if isinstance(groups, dict):
        groups = [groups]

    for group in groups:
        if group.get('name') == name:
            return group.get('objectId')

    return None


def add_group(client_session, scopeId, name, member, excludeMember,
              dynamicMemberDefinition):

    security_group = {
        'securitygroup': {
            'name': name,
            'member': member,
            'excludeMember': excludeMember,
            'dynamicMemberDefinition': dynamicMemberDefinition
        }
    }

    raw_result = client_session.create(
        'secGroupBulk', uri_parameters={'scopeId': scopeId},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return raw_result['objectId']


def add_group_exclude_member(client_session, security_group_id, member_id):
    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'excludeMember' not in security_group['securitygroup']:
        security_group['securitygroup']['excludeMember'] = []

    excludeMembers = security_group['securitygroup']['excludeMember']
    if isinstance(excludeMembers, dict):
        excludeMembers = [excludeMembers]

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            raise cfy_exc.NonRecoverableError(
                "Member %s already exists in %s" % (
                    member_id, security_group['securitygroup']['name']
                )
            )

    excludeMembers.append({"objectId": member_id})

    security_group['securitygroup']['excludeMember'] = excludeMembers

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def add_group_member(client_session, security_group_id, member_id):

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'member' not in security_group['securitygroup']:
        security_group['securitygroup']['member'] = []

    members = security_group['securitygroup']['member']
    if isinstance(members, dict):
        members = [members]

    for member in members:
        if member.get("objectId") == member_id:
            raise cfy_exc.NonRecoverableError(
                "Member %s already exists in %s" % (
                    member_id, security_group['securitygroup']['name']
                )
            )

    members.append({"objectId": member_id})

    security_group['securitygroup']['member'] = members

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def set_dynamic_member(client_session, security_group_id, dynamic_set):

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    # fully overwrite previous state
    security_group['securitygroup']['dynamicMemberDefinition'] = {
        'dynamicSet': dynamic_set
    }

    # it is not error!
    # We need to use bulk to update dynamic members
    # with use security_group_id as scope
    raw_result = client_session.update(
        'secGroupBulk', uri_parameters={'scopeId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return security_group_id


def del_dynamic_member(client_session, security_group_id):
    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    security_group['securitygroup']['dynamicMemberDefinition'] = {}

    # it is not error!
    # We need to use bulk to update dynamic members
    # with use security_group_id as scope
    raw_result = client_session.update(
        'secGroupBulk', uri_parameters={'scopeId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group_member(client_session, resource_id):
    security_group_id, member_id = resource_id.split("|")

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'member' not in security_group['securitygroup']:
        return

    members = security_group['securitygroup']['member']
    if isinstance(members, dict):
        members = [members]

    for member in members:
        if member.get("objectId") == member_id:
            members.remove(member)
            break

    security_group['securitygroup']['member'] = members

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group_exclude_member(client_session, resource_id):
    security_group_id, member_id = resource_id.split("|")

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'excludeMember' not in security_group['securitygroup']:
        return

    excludeMembers = security_group['securitygroup']['excludeMember']
    if isinstance(excludeMembers, dict):
        excludeMembers = [excludeMembers]

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            excludeMembers.remove(member)
            break

    security_group['securitygroup']['member'] = excludeMembers

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group(client_session, resource_id):

    client_session.delete('secGroupObject',
                          uri_parameters={'objectId': resource_id},
                          query_parameters_dict={'force': 'true'})
