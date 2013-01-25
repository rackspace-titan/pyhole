#   Copyright 2011 Paul Voccio
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pyhole Integration between bug tracking interfaces"""
import traceback

from lxml import etree

from launchpadlib.launchpad import Launchpad as LP

from pyhole import plugin
from pyhole import utils
from pyhole.plugins import versionone
from pyhole.plugins import launchpad


class TrackingIntegration(plugin.Plugin):

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.version_one = versionone.VersionOne(irc)
        self.launchpad = launchpad.Launchpad(irc)

    @plugin.hook_add_command("importlp")
    @utils.spawn
    def importlp(self, params=None, **kwargs):
        """Import launchpad bug into V1 importlp <lpbugnumber> <v1project>"""
        if params:
            lpid, v1project = params.split(" ", 2)
            bug = self.launchpad.launchpad.bugs[params]
            # We have info about the task now, lets import it into v1
            task = bug.bug_tasks[len(bug.bug_tasks) - 1]
            # Append the launchpad id
            desc = "<p>%s</p> <p>&nbsp;</p> <p>%s</p>" % (bug.description, 
                                                          task.web_link)
            self.version_one._v1asset('Defect', v1project, bug.title, desc)
        else:
            self.irc.reply(self.importlp.__doc__)

    @plugin.hook_add_command("addreview")
    @utils.spawn
    def addreview(self, params=None, **kwargs):
        """Adds a gerrit review link to the V1 bug/story 
           usage: addreview Defect|Story v1id gerritreview"""
        if params:
            v1id, gerritreview = params.split(" ", 2)
            typestr, v1id = v1id.split("-")
            type = versionone.V1MAPPING[typestr]
            # attrs always returns the v1id
            v1attrs = self.version_one._retrieve_asset_attributes(type,
                                                                   v1id, 
                                                                   ['Description'])
            desc = "%s <p>&nbsp;</p> <p>%s</p>" % (v1attrs[1],
                                                          gerritreview)
            # Get the v1 id from Defect:BLAH
            v1id = v1attrs[0].split(":")[1]
            self.version_one._update(type, v1id, "Description", desc)
        else:
            self.irc.reply(self.importlp.__doc__)
