#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "certified"}

DOCUMENTATION = r"""
---
module: aci_oob_contract
short_description: Manage out-of-band contract resources (vz:OOBBrCP)
description:
- Manage out-of-band Contract resources on Cisco ACI fabrics.
options:
  contract:
    description:
    - The name of the contract.
    type: str
    aliases: [ contract_name, name ]
  description:
    description:
    - Description for the contract.
    type: str
    aliases: [ descr ]
  scope:
    description:
    - The scope of a service contract.
    - The APIC defaults to C(context) when unset during creation.
    type: str
    choices: [ application-profile, context, global, tenant ]
  priority:
    description:
    - The desired QoS class to be used.
    - The APIC defaults to C(unspecified) when unset during creation.
    type: str
    choices: [ level1, level2, level3, unspecified ]
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
extends_documentation_fragment:
- cisco.aci.aci
- cisco.aci.annotation
- cisco.aci.owner

seealso:
- name: APIC Management Information Model reference
  description: More information about the internal APIC class B(vz:BrCP).
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Faiz Mohammad (@faizmoh)
"""

EXAMPLES = r"""
- name: Add a new contract
  cisco.aci.aci_oob_contract:
    host: apic
    username: admin
    password: SomeSecretPassword
    contract: web_to_db
    description: Communication between web-servers and database
    scope: global
    state: present
  delegate_to: localhost

- name: Remove an existing contract
  cisco.aci.aci_contract:
    host: apic
    username: admin
    password: SomeSecretPassword
    contract: web_to_db
    state: absent
  delegate_to: localhost

- name: Query a specific contract
  cisco.aci.aci_contract:
    host: apic
    username: admin
    password: SomeSecretPassword
    contract: web_to_db
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all contracts
  cisco.aci.aci_contract:
    host: apic
    username: admin
    password: SomeSecretPassword
    state: query
  delegate_to: localhost
  register: query_result
"""

RETURN = r"""
current:
  description: The existing configuration from the APIC after the module has finished
  returned: success
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production environment",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
error:
  description: The error information as returned from the APIC
  returned: failure
  type: dict
  sample:
    {
        "code": "122",
        "text": "unknown managed object class foo"
    }
raw:
  description: The raw output returned by the APIC REST API (xml or json)
  returned: parse error
  type: str
  sample: '<?xml version="1.0" encoding="UTF-8"?><imdata totalCount="1"><error code="122" text="unknown managed object class foo"/></imdata>'
sent:
  description: The actual/minimal configuration pushed to the APIC
  returned: info
  type: list
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment"
            }
        }
    }
previous:
  description: The original configuration from the APIC before the module has started
  returned: info
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
proposed:
  description: The assembled configuration from the user-provided parameters
  returned: info
  type: dict
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment",
                "name": "production"
            }
        }
    }
filter_string:
  description: The filter string used for the request
  returned: failure or debug
  type: str
  sample: ?rsp-prop-include=config-only
method:
  description: The HTTP method used for the request to the APIC
  returned: failure or debug
  type: str
  sample: POST
response:
  description: The HTTP response from the APIC
  returned: failure or debug
  type: str
  sample: OK (30 bytes)
status:
  description: The HTTP status from the APIC
  returned: failure or debug
  type: int
  sample: 200
url:
  description: The HTTP url used for the request to the APIC
  returned: failure or debug
  type: str
  sample: https://10.11.12.13/api/mo/uni/tn-production.json
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.aci.plugins.module_utils.aci import ACIModule, aci_argument_spec, aci_annotation_spec, aci_owner_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(aci_annotation_spec())
    argument_spec.update(aci_owner_spec())
    argument_spec.update(
        contract=dict(type="str", aliases=["contract_name", "name"]),  # Not required for querying all objects
        description=dict(type="str", aliases=["descr"]),
        scope=dict(type="str", choices=["application-profile", "context", "global", "tenant"]),
        priority=dict(type="str", choices=["level1", "level2", "level3", "unspecified"]),  # No default provided on purpose
        state=dict(type="str", default="present", choices=["absent", "present", "query"]),
        name_alias=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["contract"]],
            ["state", "present", ["contract"]],
        ]
    )

    contract = module.params.get("contract")
    description = module.params.get("description")
    scope = module.params.get("scope")
    priority = module.params.get("priority")
    state = module.params.get("state")
    tenant = "mgmt"     # hard coding tenant to 'mgmt'
    name_alias = module.params.get("name_alias")

    aci = ACIModule(module)
    aci.construct_url(
        root_class=dict(
            aci_class="fvTenant",
            aci_rn="tn-{0}".format(tenant),
            module_object=tenant,
            target_filter={"name": tenant},
        ),
        subclass_1=dict(
            aci_class="vzOOBBrCP",
            aci_rn="oobbrc-{0}".format(contract),
            module_object=contract,
            target_filter={"name": contract},
        ),
    )

    aci.get_existing()

    if state == "present":
        aci.payload(
            aci_class="vzOOBBrCP",
            class_config=dict(
                name=contract,
                descr=description,
                scope=scope,
                prio=priority,
                nameAlias=name_alias,
            ),
        )

        aci.get_diff(aci_class="vzOOBBrCP")

        aci.post_config()

    elif state == "absent":
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()