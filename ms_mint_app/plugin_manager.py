import logging

from pkg_resources import iter_entry_points
from collections import OrderedDict

from .plugin_interface import PluginInterface

# Import built-in plugins
from .plugins.workspaces import WorkspacesPlugin  
from .plugins.ms_files import MsFilesPlugin
from .plugins.metadata import MetadataPlugin
from .plugins.targets import TargetsPlugin
from .plugins.add_metabolites import AddMetabolitesPlugin
from .plugins.target_optimization import TargetOptimizationPlugin
from .plugins.processing import ProcessingPlugin
from .plugins.quality_control import QualityControlPlugin
from .plugins.analysis import AnalysisPlugin


class PluginManager:
    def __init__(self):
        self.plugins = OrderedDict()
        self.discover_plugins()

    def discover_plugins(self):
        # Register built-in plugins with order attribute
        self.register_plugin("Workspaces", WorkspacesPlugin())
        self.register_plugin("MS-Files", MsFilesPlugin())
        self.register_plugin("Metadata", MetadataPlugin())
        self.register_plugin("Targets", TargetsPlugin())
        #self.register_plugin("Add Metabolites", AddMetabolitesPlugin())
        self.register_plugin("Optimization", TargetOptimizationPlugin())
        self.register_plugin("Processing", ProcessingPlugin())
        self.register_plugin("Quality Control", QualityControlPlugin())
        self.register_plugin("Analysis", AnalysisPlugin())


        # Discover and register external plugins
        for entry_point in iter_entry_points("ms_mint_app.plugins"):
            plugin = entry_point.load()
            plugin_name = entry_point.name
            plugin_instance = plugin()
            self.register_plugin(plugin_name, plugin_instance)

    def register_plugin(self, plugin_name, plugin_instance):
        self.plugins[plugin_name] = plugin_instance

    def get_plugins(self):
        plugins = sorted(self.plugins.values(), key=lambda x: x.order)
        return {plugin.label: plugin for plugin in plugins}
