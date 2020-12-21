import os

from cloudify import ctx
from cloudify.decorators import operation

@operation
def list_directory_files(ctx, **kwargs):
    path_to_list_files = ctx.node.properties.get('directory_path', "")
    files = ",".join(os.listdir(path_to_list_files))
    ctx.instance.runtime_properties['data'] = files
