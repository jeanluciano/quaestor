{
  description = "Flake Template: Template for working with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    flake-utils,
    ...
  } @ inputs: let
    projectName = "flake_template";
  in
    (flake-utils.lib.eachDefaultSystem (system: let
      uvBoilerplate = import nix/uv.nix {inherit inputs system projectName;};
      inherit
        (uvBoilerplate)
        pythonSet
        workspace
        ;
    in
      with uvBoilerplate; {
        # Provide the package
        # No opt dependencies for production
        packages.default = pythonSet.mkVirtualEnv "${projectName}-env" workspace.deps.default;

        # Make the project runnable with `nix run`
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/${projectName}";
        };

        # Make pytest available through nix flake check
        checks = {inherit (pythonSet.${projectName}.passthru.tests) pytest;};

        devShells = import nix/shell.nix {inherit inputs uvBoilerplate projectName;};
      }))
    // {
      # overlays.default = import nix/overlay.nix;
      # homeManagerModules.default = import nix/hm.nix;
    };
}
