from rbtools.commands import Command, CommandError, Option
from rbtools.utils.diffs import get_diff


class Diff(Command):
    """Prints a diff to the terminal."""
    name = "diff"
    author = "The Review Board Project"
    args = "[revisions]"
    option_list = [
        Option("--server",
               dest="server",
               metavar="SERVER",
               config_key="REVIEWBOARD_URL",
               default=None,
               help="specify a different Review Board server to use"),
        Option('--revision-range',
               dest='revision_range',
               default=None,
               help='generate a diff with the given revision range '
                    '(DEPRECATED'),
        Option('-I', '--include',
               dest='include_files',
               action='append',
               help='include only the given file in the diff (can be used '
                    'multiple times)'),
        Option("--parent",
               dest="parent_branch",
               metavar="PARENT_BRANCH",
               help="the parent branch this diff should be against "
                    "(only available if your repository supports "
                    "parent diffs)"),
        Option("--tracking-branch",
               dest="tracking",
               metavar="TRACKING",
               help="Tracking branch from which your branch is derived "
                    "(git only, defaults to origin/master)"),
        Option("--p4-client",
               dest="p4_client",
               config_key="P4_CLIENT",
               default=None,
               help="the Perforce client name that the review is in"),
        Option("--p4-port",
               dest="p4_port",
               config_key="P4_PORT",
               default=None,
               help="the Perforce servers IP address that the review is on"),
        Option("--p4-passwd",
               dest="p4_passwd",
               config_key="P4_PASSWD",
               default=None,
               help="the Perforce password or ticket of the user "
                    "in the P4USER environment variable"),
        Option("--svn-show-copies-as-adds",
               dest="svn_show_copies_as_adds",
               metavar="y/n",
               default=None,
               help="don't diff copied or moved files with their source"),
        Option('--svn-changelist',
               dest='svn_changelist',
               default=None,
               help='generate the diff for review based on a local SVN '
                    'changelist'),
        Option("--repository",
               dest="repository_name",
               config_key="REPOSITORY",
               default=None,
               help="the name of the repository configured on Review Board "
                    "that matches the local repository"),
        Option("--repository-url",
               dest="repository_url",
               help="the url for a repository for creating a diff "
                    "outside of a working copy (currently only "
                    "supported by Subversion with specific revisions or "
                    "--diff-filename and ClearCase with relative "
                    "paths outside the view). For git, this specifies"
                    "the origin url of the current repository, "
                    "overriding the origin url supplied by the git "
                    "client."),
        Option("--username",
               dest="username",
               metavar="USERNAME",
               config_key="USERNAME",
               default=None,
               help="user name to be supplied to the Review Board server"),
        Option("--password",
               dest="password",
               metavar="PASSWORD",
               config_key="PASSWORD",
               default=None,
               help="password to be supplied to the Review Board server"),
        Option('--repository-type',
               dest='repository_type',
               config_key="REPOSITORY_TYPE",
               default=None,
               help='the type of repository in the current directory. '
                    'In most cases this should be detected '
                    'automatically but some directory structures '
                    'containing multiple repositories require this '
                    'option to select the proper type. Valid '
                    'values include bazaar, clearcase, cvs, git, '
                    'mercurial, perforce, plastic, and svn.'),
    ]

    def main(self, *args):
        """Print the diff to terminal."""
        # The 'args' tuple must be made into a list for some of the
        # SCM Clients code. See comment in post.
        args = list(args)

        if self.options.revision_range:
            raise CommandError(
                'The --revision-range argument has been removed. To create a '
                'diff for one or more specific revisions, pass those '
                'revisions as arguments. For more information, see the '
                'RBTools 0.6 Release Notes.')

        if self.options.svn_changelist:
            raise CommandError(
                'The --svn-changelist argument has been removed. To use a '
                'Subversion changelist, pass the changelist name as an '
                'additional argument after the command.')

        repository_info, tool = self.initialize_scm_tool(
            client_name=self.options.repository_type)
        server_url = self.get_server_url(repository_info, tool)
        api_client, api_root = self.get_api(server_url)
        self.setup_tool(tool, api_root=api_root)

        diff_info = get_diff(
            tool,
            repository_info,
            revision_spec=args,
            files=self.options.include_files)

        diff = diff_info['diff']

        if diff:
            print diff
