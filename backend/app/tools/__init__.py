from app.tools.filesystem.list_directory import list_directory_tool
from app.tools.filesystem.read_file import read_file_tool
from app.tools.filesystem.write_file import write_file_tool
from app.tools.registry import tool_registry
from app.tools.filesystem.search_files import search_files_tool

tool_registry.register(search_files_tool)
tool_registry.register(list_directory_tool)
tool_registry.register(read_file_tool)
tool_registry.register(write_file_tool)
