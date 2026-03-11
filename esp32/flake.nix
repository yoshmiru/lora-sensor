{
  description = "MicroPython development environment for ESP32";

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
            python3
            python3Packages.mpremote
            esptool
          ];

          shellHook = ''
            echo "--- ESP32 MicroPython Dev Environment ---"
            echo "Available tools:"
            echo "  - mpremote: File transfer and REPL"
            echo "  - esptool:  Flash firmware"
          '';
        };
      });
}
