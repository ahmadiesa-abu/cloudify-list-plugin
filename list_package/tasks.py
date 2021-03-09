import os

from cloudify import ctx
from cloudify.decorators import operation

@operation
def list_directory_files(ctx, directory_path, **kwargs):
    files = ",".join(os.listdir(directory_path))
    ctx.instance.runtime_properties['data'] = files
