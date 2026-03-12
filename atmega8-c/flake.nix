{
  description = "C development environment for ATmega8 (AVR)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pkgsCross.avr.buildPackages.gcc
            pkgsCross.avr.buildPackages.binutils
            avrdude
            gnumake
          ];

          shellHook = ''
            echo "--- ATmega8 C Development Environment ---"
            avr-gcc --version
          '';
        };
      });
}
