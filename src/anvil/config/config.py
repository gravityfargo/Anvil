# def set_s_project(self, project_name: str):
#     p = Printer("function", "set_s_project()")
#     if project_name == self.s_project["name"]:
#         p.ok("already set")
#         return
#     elif project_name not in list(self.projects.keys()):
#         p.error("invalid")

#     self.s_project["name"] = project_name

#     self.set_s_group(None)
#     p.changed(project_name)

# def set_s_group(self, group_name):
#     p = Printer("function", "set_s_group()")
#     s_group_data = {
#         "name": None,
#         "path": None,
#         "hosts": None,
#         "var_file_path": None,
#     }
#     if group_name == self.s_group["name"]:
#         p.ok("already set")
#         return

#     if group_name not in self.s_project["groups_list"]:
#         p.error("invalid")
#         group_name = None
#         self.set_s_host(None)

#     elif group_name is None:
#         p.changed("None")
#         self.set_s_host(None)

#     else:
#         s_group_data["name"] = group_name
#         s_group_data["path"] = self.s_project["groups"][group_name]["path"]
#         s_group_data["var_file_path"] = self.s_project["groups"][group_name][
#             "var_file_path"
#         ]
#         hosts = []
#         for host in self.s_project["hosts"]:
#             if self.s_project["hosts"][host]["group"] == group_name:
#                 hosts.append(host)
#         s_group_data["hosts"] = hosts

#     self.s_group = s_group_data
#     YamlManager(self.config_file).create_or_update_item("s_group", s_group_data)
#     p.changed(group_name)

# def set_s_host(self, host_name: str | None) -> None:
#     p = Printer("function", "set_s_host()")
#     s_host_data = {
#         "name": None,
#         "path": None,
#         "group": None,
#         "var_file_path": None,
#     }

#     if host_name == self.s_host["name"]:
#         p.ok("already set")
#         return

#     if self.s_project["hosts"].get(host_name) is None:
#         p.error("invalid")
#         host_name = None

#     else:
#         s_host_data["name"] = host_name
#         s_host_data["path"] = self.s_project["hosts"][host_name]["path"]
#         s_host_data["group"] = self.s_project["hosts"][host_name]["group"]
#         self.set_s_group(s_host_data["group"])
#         s_host_data["var_file_path"] = self.s_group["var_file_path"]

#     self.s_host = s_host_data
#     YamlManager(self.config_file).create_or_update_item("s_host", self.s_host)
#     p.changed(host_name)


# def sync_project_with_file_system(
#     self, config_file: str, s_project_dict: dict = None
# ) -> dict:
#     p = Printer("function", "sync_project_with_file_system()")
#     found_folders = []
#     found_items = []
#     git_config = os.path.join(s_project_dict["path"], ".git", "config")

#     for proj_root_item in os.listdir(s_project_dict["path"]):
#         if os.path.isdir(os.path.join(s_project_dict["path"], proj_root_item)):
#             found_folders.append(proj_root_item)
#         else:
#             found_items.append(proj_root_item)

#     # check for git
#     FileManager(s_project_dict["path"]).check_dir(".git")
#     FileManager(git_config).check_file()
#     with open(git_config, "r") as file:
#         content = file.read()
#         url = re.search(r"url\s*=\s*(.*)", content)
#         if url is not None:
#             s_project_dict["repo_url"] = url.group(1)

#     FileManager(s_project_dict["ansible_config_file"]).check_file()
#     FileManager(s_project_dict["inventory_file"]).check_file()
#     FileManager(s_project_dict["tree_file"]).check_file()

#     s_project_dict = self.parse_inventory_file(s_project_dict)

#     # make sure directories exist
#     for group in s_project_dict["groups"]:
#         gpath = s_project_dict["groups"][group]["path"]
#         vpath = s_project_dict["groups"][group]["var_file_path"]
#         FileManager(gpath).check_dir()
#         FileManager(vpath).check_file()

#     for host in s_project_dict["hosts_list"]:
#         hpath = s_project_dict["hosts"][host]["path"]
#         FileManager(hpath).check_dir()

#     YamlManager(config_file).create_or_update_item("s_project", s_project_dict)
#     p.ok("Success")

#     self.sync_tree_with_file_system(s_project_dict)

# def sync_tree_with_file_system(self, project_dict: dict):
#     p = Printer("function", "sync_tree_with_file_system()")
#     tree_file = project_dict["tree_file"]
#     current_tree = YamlManager(tree_file).get_all()
#     tree = {}
#     project_dir = project_dict["path"]

#     def inventory_directory(directory):
#         for item in os.listdir(directory):
#             props = {"service": None, "commands": []}
#             item_path = os.path.join(directory, item)
#             if os.path.isdir(item_path):
#                 inventory_directory(item_path)
#             else:
#                 key = item_path.replace(project_dir, "")[1:]
#                 if current_tree.get(key) is not None:
#                     if current_tree[key] != props:
#                         props = current_tree[key]
#                 if key.endswith("_vars.yaml"):
#                     continue
#                 tree[key] = props

#     for group in project_dict["groups_list"]:
#         group_path = os.path.join(project_dir, group)
#         if os.path.isdir(group_path):
#             inventory_directory(group_path)

#     YamlManager(tree_file).save_all(tree)
#     p.ok("Success")

# def parse_inventory_file(self, s_project_dict: dict) -> dict:
# s_project = {
#     "allgroups_content": {},
#     "all_pass": False,
#     "groups": {},
#     "groups_list": [],
#     "hosts": {},
#     "hosts_list": [],
# }

# inv_file_contents = YamlManager(s_project_dict["inventory_file"]).get_all()

# def process_content(inv_file_contents):
#     nonlocal s_project

#     for group, value in inv_file_contents.items():
#         group_data = {
#             "hosts": [],
#             "var_file_path": None,
#             "path": None,
#         }
#         if group == "all" and not s_project["all_pass"]:
#             s_project["all_groups_content"] = inv_file_contents["all"]["vars"][
#                 "anvil_all_groups"
#             ]
#             s_project["all_pass"] = True
#             process_content(s_project["all_groups_content"])
#             continue

#         group_data["path"] = os.path.join(s_project_dict["path"], group)
#         if group.startswith("all"):
#             group_data.pop("hosts")
#             vars_dict = s_project["all_groups_content"][group].get("vars")
#         else:
#             vars_dict = inv_file_contents[group].get("vars")
#             for host in inv_file_contents[group]["hosts"].keys():
#                 host_data = {
#                     "group": None,
#                     "path": None,
#                 }
#                 group_data["hosts"].append(host)
#                 host_data["path"] = os.path.join(
#                     s_project_dict["path"], group, host
#                 )
#                 host_data["group"] = group

#                 s_project["hosts"][host] = host_data
#                 s_project["hosts_list"].append(host)

#         if vars_dict is not None:
#             group_data["var_file_path"] = vars_dict["anvil_variable_file"]

#         if group_data["var_file_path"] is not None:
#             group_data["var_file_path"] = os.path.join(
#                 s_project_dict["path"], group, group_data["var_file_path"]
#             )

#         s_project["groups_list"].append(group)
#         s_project["groups"][group] = group_data

# process_content(inv_file_contents)

# s_project_dict["groups"] = s_project["groups"]
# s_project_dict["groups_list"] = s_project["groups_list"]
# s_project_dict["hosts"] = s_project["hosts"]
# s_project_dict["hosts_list"] = s_project["hosts_list"]

# return s_project_dict
