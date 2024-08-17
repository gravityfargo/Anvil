import json

from ansible_runner import run
from PySide6.QtCore import SignalInstance

from anvil.helpers import datautils

from .play_builder import PlayBuilder

# from anvil.config import Project, ProjectData


def anvilrun(play: PlayBuilder, progress_callback: SignalInstance):
    run_args = play.get_run_args()
    run(
        **run_args,
        event_handler=event_handler(progress_callback),
    )
    # status_handler=status_handler,


def status_handler(status_data, runner_config):
    pass
    # status_data.pop("env", None)
    # status_data.pop("runner_ident", None)
    # status_data.pop("command", None)
    # status_data.pop("cwd", None)


def event_handler(progress_callback):
    adhoc = False
    started = False
    badkeys = [
        "uuid",
        "play_uuid",
        "parent_uuid",
        "playbook_uuid",
        "task_uuid",
        "counter",
        "stdout",
        "start_line",
        "end_line",
        "runner_ident",
        "created",
        "pid",
        "ad_hoc_command_id",
        "start",
        "end",
        "duration",
    ]

    def handler(data):
        nonlocal badkeys
        nonlocal adhoc
        nonlocal started

        pc = progress_callback
        progress = {"text": "", "color": "black", "charformat": "text"}

        if data.get("event_data") is None:
            return

        event = data["event"]
        event_data = datautils.remove_empty_keys(data["event_data"])

        for key in badkeys:
            event_data.pop(key, None)

        print(event)
        print(json.dumps(event_data, indent=2))

        match event:
            case "playbook_on_start":
                # progress["text"] = "Started"
                # progress["color"] = "black"
                # progress["charformat"] = "h1"

                if data["event_data"]["playbook"] == "__adhoc_playbook__":
                    progress["text"] = "Adhoc Playbook"
                    progress["color"] = "purple"
                    progress["charformat"] = "h2"
                    adhoc = True

            case "playbook_on_play_start":
                # playbook
                progress["text"] = "Playbook Started"
                progress["color"] = "purple"
                progress["charformat"] = "h2"
                pc.emit(progress)
                progress["color"] = "black"
                progress["charformat"] = "h3"
                progress["text"] = f"Target(s):\n\t{data["event_data"]["play_pattern"]}"

            case "playbook_on_task_start":
                # "task": "Gathering Facts",
                progress["text"] = data["event_data"]["task"]
                progress["color"] = "cyan"
                progress["charformat"] = "h2"

            case "runner_on_start":
                # ping,
                if adhoc:
                    # "resolved_action": "ansible.builtin.ping",
                    progress["text"] = data["event_data"]["resolved_action"]
                    progress["color"] = "cyan"
                    progress["charformat"] = "h3"
                    pc.emit(progress)
                    adhoc = False
                progress["text"] = f"\t{data["event_data"]["host"]}"
                progress["color"] = "black"
                progress["charformat"] = "text"

            case "playbook_on_stats":
                progress["text"] = "Finished"
                pc.emit(progress)
                progress["text"] = ""

            # ERRORS
            case "runner_on_unreachable":
                progress["text"] = "Host Unreachable!"
                progress["color"] = "red"
                progress["charformat"] = "h2"
                # data["event_data"]["res"]["msg"]

        pc.emit(progress)



    return handler
    #     match event_data["event"]:
    #         case "playbook_on_start":
    #             pass
    #         case "playbook_on_play_start":
    #             pass
    #         case "playbook_on_task_start":
    #             pass
    #         case "playbook_on_include":
    #             pass
    #         case "runner_item_on_skipped":
    #             pass
    #         case "runner_on_skipped":
    #             pass
    #         case "runner_on_start":
    #             if event_data["event_data"]["task"] != last_message:

    #                 last_message = event_data["event_data"]["task"]
    #         case "runner_on_ok":

    #             #
    #             color = "green"
    #             host = ""
    #             res = event_data["event_data"]["res"]
    #             if event_data["event_data"].get("host") is not None:
    #                 host = event_data["event_data"]["host"]

    #             if "warnings" in res.keys():
    #                 for warning in res["warnings"]:
    #                     if warning is not None:
    #                         pass
    #                 res.pop("warnings", None)

    #             if res.get("results") is not None:
    #                 for i in res["results"]:
    #                     i.pop("invocation", None)
    #                     #
    #                     if i["changed"]:
    #                         color = "yellow"
    #                     if i.get("path") is not None:
    #                         pass
    #                     if i.get("dest") is not None:
    #                         pass
    #             else:
    #                 if res["changed"]:
    #                     color = "yellow"
    #                 if res.get("path") is not None:
    #                     pass
    #                 if res.get("path") is not None:
    #                     pass
    #         case "runner_item_on_ok":
    #             #

    #             color = "green"
    #             if event_data["event_data"]["res"]["changed"]:
    #                 color = "yellow"

    #             # if event_data["event_data"]["res"].get("path") is not None:
    #             #
    #         case "runner_on_unreachable":
    #             pass
    #         case "playbook_on_stats":
    #             pass
    #         case "runner_item_on_failed":
    #             pass
    #         case "runner_on_failed":
    #             pass

    #         case "verbose":
    #             pass  # Explicitly do nothing for 'verbose'
    #         case _:
    #             pass

    # return handler
