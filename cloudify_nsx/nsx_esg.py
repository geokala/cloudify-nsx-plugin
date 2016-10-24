########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from cloudify import ctx
from cloudify.decorators import operation
import pynsxv.library.nsx_esg as nsx_esg
from nsx_common import nsx_login
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    edge_dict = properties.get('edge', {})
    edge_dict.update(kwargs.get('edge', {}))
    use_existed = edge_dict.get('use_external_resource', False)

    ctx.logger.info("checking %s" % str(edge_dict["name"]))

    resource_id, _ = nsx_esg.esg_read(client_session, str(edge_dict["name"]))
    if use_existed:
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("Used existed %s" % str(resource_id))
        return
    if resource_id:
        raise cfy_exc.NonRecoverableError(
            "We already have such router"
        )

    resource_id, location = nsx_esg.esg_create(client_session,
        str(edge_dict['name']),
        str(edge_dict['esg_pwd']),
        str(edge_dict['esg_size']),
        str(edge_dict['datacentermoid']),
        str(edge_dict['datastoremoid']),
        str(edge_dict['resourcepoolid']),
        str(edge_dict['default_pg']),
        str(edge_dict['esg_username']),
        str(edge_dict['esg_remote_access'])
    )
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (str(resource_id), str(location)))


@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    nsx_esg = properties.get('edge', {})
    nsx_esg.update(kwargs.get('edge', {}))
    use_existed = nsx_esg.get('use_external_resource', False)

    ctx.logger.info("checking %s" % str(nsx_esg["name"]))

    resource_id, _ = nsx_esg.esg_read(client_session, str(nsx_esg["name"]))
    if use_existed:
        ctx.logger.info("Used existed %s" % str(resource_id))
        return

    status, resource_id = nsx_esg.esg_delete(client_session, str(nsx_esg['name']))
    if not status:
        raise cfy_exc.NonRecoverableError(
            "Can't drop router."
        )
    ctx.logger.info("delete %s" % resource_id)