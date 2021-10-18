import os
import json
import tempfile
from contextlib import contextmanager

from cloudify import ctx
from cloudify.decorators import operation

"""Param name for available secrets"""
SUPPLIED_SECRETS_PARAM = 'supplied_secrets'
UPDATED_SECRET_PARAM = 'updated_secret'


@operation
def list_directory_files(ctx, **kwargs):
    directory_path = ctx.node.properties.get('directory_path', "")
    files = ",".join(os.listdir(directory_path))
    ctx.instance.runtime_properties['data'] = files


def params(day2_redeploy=True, include_secrets=False):
    """
    :return: dict Copy of current operation's day2 params and secrets combined
    """
    from cloudify.state import ctx_parameters as ctx_p
    if not day2_redeploy:
        fn.set_properties_from_dict(ctx_p)

    result = dict(ctx.instance.runtime_properties)

    # Load secrets if any
    if include_secrets and SUPPLIED_SECRETS_PARAM in ctx_p:
        for secret_id in ctx_p[SUPPLIED_SECRETS_PARAM]:
            result[secret_id] = secret(secret_id)

    if UPDATED_SECRET_PARAM in ctx_p:
        result[UPDATED_SECRET_PARAM] = ctx_p[UPDATED_SECRET_PARAM]

    return result


@contextmanager
def _temp_file():
    """
    Context manager for temporary file.
    """
    f_handle, f_path = tempfile.mkstemp()
    # Close OS-level file handle since not needed
    os.close(f_handle)
    try:
        yield f_path
    finally:
        os.remove(f_path)


@operation
def ps1(script_path, process=None, include_secrets=False, **kwargs):
    """
    Wraps original PowerShell caller with Cloudify ENV and Params()

    Usage:

    In blueprint:

        interfaces:
          cloudify.interfaces.day2:
            custom_operation:
              implementation: listp.list_package.tasks.ps1
              inputs:
                script_path: scripts/custom_operation.ps1
                ...env, args, whatever

    Runtime properties are passed to PowerShell script via JSON file.
    PowerShell has to include following to read in runtime properties from JSONfile.

        Param($paramsJson,$params=$(Get-Content -Raw -Path $paramsJson | ConvertFrom-Json))
    """
    from script_runner.tasks import run

    if not process:
        process = {}

    with _temp_file() as props_json:
        with open(props_json, 'w') as fd:
            fd.write(json.dumps(params(include_secrets=include_secrets), indent=4))

        process['command_prefix'] = process.get('command_prefix', 'powershell')
        process['args'] = process.get('args', []) + ["-paramsJson", props_json]

        if 'env' not in process:
            process['env'] = {}
        process['env']['PATH'] = process['env'].get('Path', os.environ['Path']) \
                                 + r';C:\Salt;C:\Program Files (x86)\GNU\GnuPG\pub'

        return run(script_path, process, **kwargs)
