{
  description = "tts-backup";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-21.05";
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, utils }:
    (utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: {
              tts-backup = final.callPackage ./nix/tts-backup.nix { };
            })
          ];
        };
      in rec {
        packages = rec {
          default = tts-backup;
          tts-backup = pkgs.tts-backup;
        };
        apps = rec {
          tts-backup = {
            type = "app";
            program = "${packages.tts-backup}/bin/tts-backup";
          };
          tts-prefetch = {
            type = "app";
            program = "${packages.tts-backup}/bin/tts-prefetch";
          };
          default = tts-backup;
        };
      }));
}
