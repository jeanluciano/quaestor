# Dev Shells
{
  inputs,
  uvBoilerplate,
  projectName,
  ...
}: let
  # From the boilerplate, pull in what we need
  inherit
    (uvBoilerplate)
    lib
    pkgs
    workspace
    pythonSet
    python
    ;

  standartPackages = with uvBoilerplate.pkgs; [
    # Unix utilities
    coreutils # Basic file, shell and text manipulation utilities
    findutils # Find, locate, and xargs commands
    gnugrep # GNU grep, egrep and fgrep
    gnused # GNU stream editor
    ripgrep # Fast line-oriented search tool
    fd # Simple, fast and user-friendly alternative to find
    bat # Cat clone with syntax highlighting
    eza # Modern replacement for ls
    htop # Interactive process viewer
    jq # Lightweight JSON processor
    watch # Execute a program periodically
    curl # Command line tool for transferring data
    wget # Internet file retriever
    tree # Display directories as trees
    unzip # Unzip utility
    zip # Zip utility
  ];
in {
  # The default shell, where nix manages the venv and dependencies
  # The venv is editable for the local projects
  default = let
    # This overlay enables editable mode for all local dependencies
    editableOverlay = workspace.mkEditablePyprojectOverlay {
      # Pull in the environment var
      root = "$REPO_ROOT";
      # Optional; only enable editable for certain packages
      # members = [ projectName ];
    };

    # Override previous python set with the overrideable overlay
    editablePythonSet = pythonSet.overrideScope (
      lib.composeManyExtensions [
        editableOverlay

        # Apply fixups for building an editable package of your workspace packages
        (final: prev: {
          ${projectName} = prev.${projectName}.overrideAttrs (old: {
            # It's a good idea to filter the sources going into an editable build
            # so the editable package doesn't have to be rebuilt on every stage
            src = lib.fileset.toSource {
              root = old.src;
              fileset = lib.fileset.unions [
                (old.src + "/pyproject.toml")
                (old.src + "/README.md")
                (old.src + "/src/${projectName}/__init__.py")
              ];
            };

            # Hatchling (build system) has a dependency on the editables package when building editables
            # In normal python flows this dependency is dynamically handled, in PEP660
            # With Nix, the dependency needs to be explicitly declared
            nativeBuildInputs =
              old.nativeBuildInputs
              ++ final.resolveBuildSystem {
                editables = [];
              };
          });
        })
      ]
    );

    # Build our editable python to a virtual environment
    # All optional dependencies are asked for in development
    virtualenv = editablePythonSet.mkVirtualEnv "${projectName}-dev-env" workspace.deps.all;
  in (
    pkgs.mkShell {
      packages =
        standartPackages
        ++ [virtualenv pkgs.uv]
        ++ [
          # Add additional shell projects here
        ];

      env = {
        # Don't create venv using uv
        UV_NO_SYNC = "1";

        # Force uv to use Python interpreter from venv
        UV_PYTHON = python.interpreter;

        # Prevent uv from downloading managed Python's
        UV_PYTHON_DOWNLOADS = "never";
      };

      shellHook = ''
        # Undo dependency propagation by nixpkgs.
        unset PYTHONPATH

        # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
        export REPO_ROOT=$(git rev-parse --show-toplevel)
      '';
    }
  );
}
