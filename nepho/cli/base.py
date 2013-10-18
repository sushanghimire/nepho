#!/usr/bin/env python
from cement.core import backend, foundation, controller
from os import path, makedirs
import re

defaults = backend.defaults('nepho')
defaults['nepho']['archive_dir']           = path.join(path.expanduser("~"), ".nepho", "archive")
defaults['nepho']['tmp_dir']               = path.join(path.expanduser("~"), ".nepho", "tmp")
defaults['nepho']['cloudlet_dirs']         = path.join(path.expanduser("~"), ".nepho", "cloudlets")
defaults['nepho']['local_dir']             = path.join(path.expanduser("~"), ".nepho", "local")
defaults['nepho']['cloudlet_registry_url'] = "https://cloudlets.github.io/registry.yaml"


class NephoBaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = "Command line cross-cloud orchestration tool for constructing virtual datacenters."
        usage = "nepho <command> <action> [options]"

    def _setup(self, app):
        super(NephoBaseController, self)._setup(app)

        # Multiple cloudlet dirs in a string need to be split into a list and
        # excess whitespace removed
        cloudlet_dirs = self.config.get('nepho', 'cloudlet_dirs').split(',')
        cloudlet_dirs = map(lambda x: x.strip(), cloudlet_dirs)
        self.config.set('nepho', 'cloudlet_dirs', cloudlet_dirs)

        # Do some pre-processing on all configuration items
        for key in self.config.keys('nepho'):
            value = self.config.get('nepho', key)

            if isinstance(value, list):
                # Expand user where necessary
                value = map(lambda x: path.expanduser(x), value)
                self.config.set('nepho', key, value)

                # If items is are directories, make sure they exist
                if re.search('_dirs$', key):
                    for one_dir in value:
                        if not path.exists(one_dir):
                            makedirs(one_dir)
            else:
                # Expand user where necessary
                self.config.set('nepho', key, path.expanduser(value))

                # If item is a directory, make sure it exists
                if re.search('_dir$', key) and not path.exists(value):
                    makedirs(value)

        self.my_shared_obj = dict()

    @controller.expose(hide=True)
    def default(self):
        if self._meta.label == "base":
            print "Run %s --help for a list of commands" % (self.app.args.prog)

        else:
            print "Run %s %s --help for a list of actions" % (self.app.args.prog, self._meta.label)


class Nepho(foundation.CementApp):
    class Meta:
        label = 'nepho'
        base_controller = NephoBaseController
        config_defaults = defaults
