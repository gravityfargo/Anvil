import json

from ansible_runner import run
from PySide6.QtCore import SignalInstance

from anvil.helpers import datautils

from .parse_event import EventParser
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

        if data.get("event_data") is None:
            return

        ep = EventParser(progress_callback)
        ep.debug = False

        event = data["event"]
        event_data = datautils.remove_empty_keys(data["event_data"])

        for key in badkeys:
            event_data.pop(key, None)

        if event_data["playbook"] == "__adhoc_playbook__":
            match event:
                case "runner_on_start":
                    json_print = False
                    if not EventParser.oneshot:
                        EventParser.oneshot = True
                        ep.text = event_data["resolved_action"]
                        ep.color = "cyan"
                        ep.charformat = "h3"
                        ep.emit()

                case "runner_on_ok":
                    json_print = False
                    if event_data["res"]["changed"]:
                        ep.color = "yellow"
                    else:
                        ep.color = "green"
                    ep.charformat = "h3"
                    ep.skip_newline = True
                    ep.text = "OK\t"
                    ep.emit()
                    ep.text = event_data["host"]
                    ep.emit()

        else:
            ep.key = event
            match event:
                case "playbook_on_start":
                    json_print = False
                    ep.text = "Playbook Started"
                    ep.color = "purple"
                    ep.charformat = "h2"
                    ep.emit()

                case "playbook_on_task_start":
                    json_print = False
                    ep.text = event_data["name"]
                    ep.emit()

                case "runner_on_start":
                    json_print = False

                case "runner_on_ok":
                    if event_data["task"] == "Gathering Facts":
                        # OS type for package installation can be determined here
                        return

                    if event_data["task_action"] == "ansible.builtin.command":
                        # I want to print the debug message, not just OK
                        if event_data["res"]["stdout"]:
                            ep.color = "green"
                            ep.text = "Success"
                            ep.emit()

                            print(json.dumps(event_data, indent=2))

                            if event_data["task"].startswith("$ systemctl"):
                                ep.emit_systemctl(event_data["res"]["stdout_lines"])
                                return

                            ep.emit_stdout(event_data["res"]["stdout_lines"])

                        if event_data["res"]["stderr"]:
                            ep.emit(text="Failed", color="red")
                            ep.emit_stderr(event_data["res"]["stderr_lines"])

                    else:
                        if event_data["res"]["changed"]:
                            ep.color = "yellow"
                        else:
                            ep.color = "green"
                        ep.charformat = "h3"
                        ep.skip_newline = True
                        ep.text = "OK\t"
                        ep.emit()
                        ep.text = event_data["host"]
                        ep.emit()

                case "runner_on_failed":
                    ep.emit(text="Failed", color="red")

                    if event_data["res"].get("msg") is not None:
                        ep.emit(text=event_data["res"]["msg"])
                    if event_data["res"]["stderr"]:
                        ep.emit_stderr(event_data["res"]["stderr_lines"])

        match event:
            case "playbook_on_stats":
                ep.text = "Finished"
                ep.emit()

            case "runner_on_unreachable":
                ep.color = "red"
                ep.text = "Unreachable"
                ep.emit()
                print(json.dumps(event_data, indent=2))

        # if json_print:
        #     print()
        #     print(event)
        # print(json.dumps(event_data, indent=2))
        # else:
        #

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
