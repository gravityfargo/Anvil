DEFAULT_CLI_ARGS = {
    "-s": {
        "DESC": "Select a Project, Group, and or Host for manipulation",
        "USEAGE": "-sp <project_name>\n -sh <host_name>\n -sg <group_name>",
        "p": {
            "DESC": "Select a Project",
            "USEAGE": "-sp <project_name>",
        },
        "h": {
            "DESC": "Select a Host",
            "USEAGE": "-sh <host_name>",
        },
        "g": {
            "DESC": "Select a Group",
            "USEAGE": "-sg <group_name>",
        },
    },
    "-d": {
        "DESC": "Delete a Host, Group, or Project",
        "USEAGE": "-dg <group_name>",
        "g": {
            "DESC": "Delete Group",
            "USEAGE": "-dg <group_name>",
        },
    },
    "-i": {
        "DESC": "Import a Project",
        "USEAGE": "-ip <project_name>",
        "p": {
            "DESC": "Import Project",
            "USEAGE": "-ip <project_name>",
        },
    },
    "-l": {
        "DESC": "List Projects, Groups, or Hosts",
        "USEAGE": "-lg  List Host Groups\n -lh List Hosts\n -lp  List Projects",
        "p": {
            "DESC": "List All Known Projects",
            "USEAGE": "-lp",
        },
        "g": {
            "DESC": "List host groups of the current project.",
            "USEAGE": "-lg",
        },
        "h": {
            "DESC": "List hosts of the current project.",
            "USEAGE": "-lh",
        },
    },
    "-u": {
        "DESC": "Update configureations based on the files present.",
        "USEAGE": "-u",
    },
    "-r": {
        "DESC": "Interact with a remote host",
        "USEAGE": "-r-fetch <target_file>\n -r-send <target_file>\n -r-service-r <service_name>\n -r-file-c",
        "-fetch": {
            "DESC": "Fetch a file from the selected host.",
            "USEAGE": "-r-fetch <target_file>",
        },
        "-send": {
            "DESC": "Send a file to the selected host.",
            "USEAGE": "-r-send <target_file>",
        },
        "-service-r": {
            "DESC": "Restart a Service",
            "USEAGE": "-r-service-r <service_name>",
        },
        "-file-create": {
            "DESC": "Create a file on the selected host",
            "USEAGE": "-r-file-create <target_file>",
        },
        "-file-copy": {
            "DESC": "Copy a file to the selected host",
            "USEAGE": "-r-file-copy <target_file>",
        },
    },
    "generic_args": (
        (
            ("--version",),
            {"action": "version", "version": "0.0.1"},
        ),
        (
            ("--debug",),
            {
                "action": "store_true",
                "help": "enable ansible-runner debug output logging (default=False)",
            },
        ),
        (
            ("--logfile",),
            {"help": "log output messages to a file (default=None)"},
        ),
    ),
}
