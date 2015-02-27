# thanks to https://github.com/akrabat/SublimeFunctionNameDisplay

import sublime
import sublime_plugin

import re
import sys
from time import time

def plugin_loaded():
    global Pref

    class Pref:
        def load(self):
            Pref.wait_time = 0.12
            Pref.time = time()
    
    Pref = Pref()
    Pref.load()

if sys.version_info[0] == 2:
    plugin_loaded()

class CSSPathStatusEventHandler(sublime_plugin.EventListener):
    # on_activated_async seems to not fire on startup
    def on_activated(self, view):
        syntax = view.settings().get('syntax')

        if (syntax is None) or (not any(ext in syntax for ext in ["CSS", "SCSS"])):
            return

        Pref.time = time()
        sublime.set_timeout(lambda:self.display_current_path(view, 'activated'), 0)

    def on_modified(self, view):
        Pref.time = time()

    # could be async, but ST2 does not support that
    def on_selection_modified(self, view):
        syntax = view.settings().get('syntax')

        if (syntax is None) or (not any(ext in syntax for ext in ["CSS", "SCSS"])):
            return

        now = time()
        if now - Pref.time > Pref.wait_time:
            sublime.set_timeout(lambda:self.display_current_path(view, 'selection_modified'), 0)
        else:
            sublime.set_timeout(lambda:self.display_current_path_delayed(view), int(1000*Pref.wait_time))
        Pref.time = now

    def display_current_path_delayed(self, view):
        now = time()
        if (now - Pref.time >= Pref.wait_time):
            self.display_current_path(view, 'selection_modified:delayed')

    def display_current_path(self, view, where):
    	view_settings = view.settings()
        if view_settings.get('is_widget'):
            return

        scope_point = view.sel()[0].begin();
        scope_point_line_number = view.rowcol(scope_point)[0] + 1
        prev_lines = view.split_by_newlines(sublime.Region(0, scope_point))
        segments = []

        for line in prev_lines:
            line_chars = view.substr(line)

            if (line_chars.count("{") != 0):
                segments.append(line_chars.replace("{", "").replace("}", "").strip())

            if (line_chars.count("}") != 0):
                del segments[-1]

        view.set_status('css_path', " >> ".join(segments))