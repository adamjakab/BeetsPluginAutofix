#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt

import importlib
import time
from optparse import OptionParser

from alive_progress import alive_bar
from beets.dbcore.query import FixedFieldSort
from beets.library import Library, Item, parse_query_parts
from beets.ui import Subcommand, decargs
from beets.util.confit import Subview
from beetsplug.autofix import common
from beetsplug.autofix.task import Task


class AutofixCommand(Subcommand):
    config: Subview = None
    lib: Library = None
    query = None
    parser: OptionParser = None

    task_ns = "beetsplug.autofix.task"
    task_registry = None

    cfg_max_exec_time = None

    exec_time_start = None

    def __init__(self, config):
        self.config = config

        cfg = self.config.flatten()
        self.cfg_max_exec_time = cfg.get("max_exec_time")

        self.parser = OptionParser(usage='beet {plg} [options] [QUERY...]'.format(
            plg=common.plg_ns['__PLUGIN_NAME__']
        ))

        self.parser.add_option(
            '-m', '--max_exec_time',
            action='store', dest='max_exec_time', type='int',
            default=self.cfg_max_exec_time,
            help=u'[default: {}] interrupt execution after this the number of seconds'.format(
                self.cfg_max_exec_time)
        )

        self.parser.add_option(
            '-v', '--version',
            action='store_true', dest='version', default=False,
            help=u'show plugin version'
        )

        super(AutofixCommand, self).__init__(
            parser=self.parser,
            name=common.plg_ns['__PLUGIN_NAME__'],
            aliases=[common.plg_ns['__PLUGIN_ALIAS__']] if common.plg_ns['__PLUGIN_ALIAS__'] else [],
            help=common.plg_ns['__PLUGIN_SHORT_DESCRIPTION__']
        )

    def func(self, lib: Library, options, arguments):
        self.lib = lib
        self.query = decargs(arguments)

        self.cfg_max_exec_time = options.max_exec_time

        if options.version:
            self.show_version_information()
            return

        self._setup_task_registry()
        self._execute_tasks_for_all_items()

    def _execute_tasks_for_all_items(self):
        self.exec_time_start = int(time.time())
        items = self._retrieve_library_items(self.query)
        done = 0
        self._say("Total number of items: {}".format(len(items)))
        with alive_bar(len(items)) as bar:
            for item in items:
                try:
                    bar(str(item))
                    self._execute_tasks_for_item(item)
                    done += 1
                except RuntimeError as err:
                    self._say(err)
                    break
                except TimeoutError:
                    self._say("Time is up! {} seconds have passed.".format(self.cfg_max_exec_time))
                    break

        self._say("Done.")
        self._say("Elaborated items: {}".format(done))

    def _execute_tasks_for_item(self, item: Item):
        needs_item_store = False
        needs_item_write = False
        items_was_removed = False
        interrupt_requested = False

        for task_name in self.task_registry.keys():
            task = self.task_registry[task_name]["instance"]
            config = self.task_registry[task_name]["config"]
            self.check_timer()

            try:
                task.setup(config, item)
                task.run()
                needs_item_store = task.needs_item_store() | needs_item_store
                needs_item_write = task.needs_item_write() | needs_item_write
                items_was_removed = task.item_was_removed()
                if items_was_removed:
                    break
            except KeyboardInterrupt:
                interrupt_requested = True
                break
            except BaseException as err:
                self._say('Task module error[{}]: {} Skipping.'.format(task_name, err))
                continue

        if not interrupt_requested:
            if items_was_removed:
                return

            if needs_item_store:
                item.store()

            if needs_item_write:
                item.try_write()

        if interrupt_requested:
            raise RuntimeError("Interrupted")

    def _setup_task_registry(self):
        self.task_registry = {}

        task_list = self.config["tasks"].keys()
        for task_name in task_list:
            config = self.config["tasks"][task_name]

            if not config["enabled"].exists() or not config["enabled"].get(bool):
                self._say("Task({}) is not enabled! Skipping.".format(task_name), log_only=True)
                continue

            try:
                task = self.get_task_class_instance(task_name)
            except ModuleNotFoundError as err:
                self._say("Task not found! {} Skipping.".format(err))
                continue
            except NotImplementedError as err:
                self._say("Bad Task({})! {} Skipping.".format(task_name, err))
                continue
            except RuntimeError as err:
                self._say(
                    "Task({}) runtime error! {} Skipping.".format(task_name,
                                                                  err))
                continue

            # Add library to task
            task.set_library(self.lib)

            self.task_registry[task_name] = {
                "instance": task,
                "config": config
            }

        self._say("The following tasks will be executed: {}".format(", ".join(list(self.task_registry.keys()))))

    def get_task_class_instance(self, module_name):
        module_name_ns = '{0}.{1}'.format(self.task_ns, module_name)

        try:
            module = importlib.import_module(module_name_ns)
        except ModuleNotFoundError as err:
            raise RuntimeError("Module load error! {}".format(err))

        task_class = None
        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, Task) and obj != Task:
                task_class = obj
                break

        if not task_class:
            raise NotImplementedError("There is no subclass of Task class in module: {}".format(module_name_ns))

        try:
            instance = task_class()
        except BaseException as err:
            raise RuntimeError("Instance creation error! {}".format(err))

        return instance

    def _retrieve_library_items(self, query=None, model_cls=Item):
        query = [] if query is None else query
        parsed_query, parsed_sort = parse_query_parts(query, model_cls)

        parsed_sort = FixedFieldSort("albumartist", ascending=True)

        self._say("Selection query[{}]: {}".format(query, parsed_query), log_only=True)
        self._say("Ordering[{}]: {}".format(query, parsed_sort), log_only=True)

        return self.lib.items(parsed_query, parsed_sort)

    def check_timer(self):
        current_time = int(time.time())
        if self.cfg_max_exec_time != 0 and current_time - self.exec_time_start > self.cfg_max_exec_time:
            raise TimeoutError("Time up!")

    def show_version_information(self):
        self._say("{pt}({pn}) plugin for Beets: v{ver}".format(
            pt=common.plg_ns['__PACKAGE_TITLE__'],
            pn=common.plg_ns['__PACKAGE_NAME__'],
            ver=common.plg_ns['__version__']
        ), log_only=False)

    @staticmethod
    def _say(msg, log_only=True, is_error=False):
        common.say(msg, log_only, is_error)
